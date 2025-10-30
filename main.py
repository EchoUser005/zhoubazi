import asyncio
import uvicorn
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from schemas import UserInput
from prompt.context_builder import BaziContextBuilder
from agents.weekly_fortune_agent import WeeklyFortuneAgent
from pydantic import BaseModel
from agents.fortune_score_agent import FortuneScoreAgent
from services.get_fortune_score import get_fortune_score, OwnerConfigNotFound
from utils.config_loader import load_owner_user_input, save_owner_user_input
import logging
import time

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log")
    ]
)

logger = logging.getLogger(__name__)

executor = ThreadPoolExecutor(max_workers=4)

app = FastAPI(
    title="周运势分析API",
    description="提供运势排盘和运势分析功能",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = WeeklyFortuneAgent()
context_builder = BaziContextBuilder()
fortune_agent = FortuneScoreAgent()


@app.get("/")
def read_root():
    return {"message": "周运势分析API", "version": "1.0.1"}


class FortunePredictInput(UserInput):
    dimension: str


@app.post("/analyze")
async def analyze_bazi(request: UserInput):
    """运势分析接口 - 同步方式"""
    try:
        loop = asyncio.get_event_loop()
        context = await loop.run_in_executor(None, context_builder.build_context, request)
        analysis_text = await loop.run_in_executor(None, agent.generate_report, context)
        return {"result": analysis_text}
    except Exception as e:
        logger.error(f"[/analyze] 错误: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/predict_fortune")
async def predict_fortune(request: FortunePredictInput):
    """运势预测打分接口 - 同步方式"""
    try:
        loop = asyncio.get_event_loop()
        base_user = UserInput(**request.model_dump(exclude={"dimension"}))
        context = await loop.run_in_executor(None, context_builder.build_context, base_user)
        result = await loop.run_in_executor(
            None,
            lambda: fortune_agent.predict_scores(context, dimension=request.dimension)
        )
        return {"result": result}
    except Exception as e:
        logger.error(f"[/predict_fortune] 错误: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/analyze/stream")
async def analyze_bazi_sse(request: UserInput):
    try:
        logger.info("[/analyze/stream] 请求开始")
        start = time.time()

        loop = asyncio.get_event_loop()

        # logger.info("[/analyze/stream] 开始构建上下文")
        # ctx_start = time.time()
        context = await loop.run_in_executor(executor, context_builder.build_context, request)
        # logger.info(f"[/analyze/stream] 上下文构建完成，耗时 {time.time() - ctx_start:.2f}s")

        async def stream_generator():
            """
            关键：处理同步生成器（stream_report）
            在线程池中逐块读取，实时 yield 给客户端
            """
            logger.info("[stream_generator] 开始流式生成")
            stream_start = time.time()
            chunk_count = 0

            try:
                logger.info("[stream_generator] 在线程池中获取生成器")
                gen = await loop.run_in_executor(executor, agent.stream_report, context)

                while True:
                    chunk = await loop.run_in_executor(
                        executor,
                        lambda g=gen: next(g, None)
                    )

                    if chunk is None:
                        break

                    if chunk:
                        chunk_count += 1
                        logger.info(f"[stream_generator] chunk #{chunk_count}: {repr(chunk[:30])}")
                        yield chunk

                logger.info(f"[stream_generator] 完成！共 {chunk_count} 个 chunk，耗时 {time.time() - stream_start:.2f}s")

            except Exception as e:
                logger.error(f"[stream_generator] 异常: {e}", exc_info=True)
                yield f"data: [ERROR] {str(e)}\n\n"

        logger.info(f"[/analyze/stream] 返回响应，准备耗时: {time.time() - start:.2f}s")

        return StreamingResponse(
            stream_generator(),
            media_type="text/plain; charset=utf-8",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            }
        )

    except Exception as e:
        logger.error(f"[/analyze/stream] 顶层异常: {e}", exc_info=True)

        async def error_gen():
            yield f"data: [FATAL ERROR] {str(e)}\n\n"

        return StreamingResponse(
            error_gen(),
            media_type="text/event-stream; charset=utf-8",
            status_code=500
        )


class GetScoreRequest(BaseModel):
    dimension: str


@app.post("/get_fortune_score")
async def get_fortune_score_api(req: GetScoreRequest):
    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(executor, get_fortune_score, req.dimension)
        return result
    except OwnerConfigNotFound:
        return JSONResponse(
            status_code=400,
            content={"error": "OWNER_CONFIG_NOT_FOUND", "message": "未找到命主配置，请先配置后重试"}
        )
    except ValueError as ve:
        return JSONResponse(status_code=400, content={"error": str(ve)})
    except Exception as e:
        logger.error(f"[/get_fortune_score] 错误: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/owner_config")
async def get_owner_config():
    try:
        loop = asyncio.get_event_loop()
        cfg = await loop.run_in_executor(executor, load_owner_user_input)
        return {"config": cfg}
    except Exception as e:
        logger.error(f"[/owner_config GET] 错误: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/owner_config")
async def set_owner_config(data: dict):
    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(executor, save_owner_user_input, data)
        return {"ok": True}
    except Exception as e:
        logger.error(f"[/owner_config POST] 错误: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/calc_bazi")
async def calc_bazi(req: UserInput):
    try:
        loop = asyncio.get_event_loop()
        ctx = await loop.run_in_executor(executor, context_builder.build_context, req)
        parts = (ctx.bazi or "").split()
        if len(parts) == 4:
            return {
                "bazi": ctx.bazi,
                "year": parts[0],
                "month": parts[1],
                "day": parts[2],
                "hour": parts[3],
            }
        return {"bazi": ctx.bazi}
    except Exception as e:
        logger.error(f"[/calc_bazi] 错误: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": str(e)})


if __name__ == "__main__":
    uvicorn.run(app,host="0.0.0.0",port=8000)