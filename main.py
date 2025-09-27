import uvicorn
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

"""
1. 定义接口，接收原始用户输入的参数模型UserInput 
2. 定义输出，直接返回AI分析结果文本
3. 运行逻辑：
    1. 接收用户输入的参数
    2. 调用context_builder.py中的build_context方法，生成BaziContext
    3. 调用agentic_analyse.py中的ai_chat方法，生成分析结果
    4. 直接返回AI生成的分析文本
"""

app = FastAPI(
    title="周运势分析API",
    description="提供运势排盘和运势分析功能",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境应该限制
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
    """
    在现有 UserInput 的基础上新增一个显式的 dimension 字段：
    取值示例：'大运' | '流年' | '流月' | '流日'
    """
    dimension: str

@app.post("/analyze")
async def analyze_bazi(request: UserInput):
    """
    运势分析接口 - 同步方式
    """
    try:
        context = context_builder.build_context(request)
        analysis_text = agent.generate_report(context)
        return {"result": analysis_text}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/predict_fortune")
async def predict_fortune(request: FortunePredictInput):
    """
    运势预测打分接口 - 同步方式
    - 调用方显式传入 dimension
    - 其他变量（包括 other_info）由服务端内部处理
    - 仅当 dimension == '流日' 时，other_info 自动注入“流日干支：{X}日”
    """
    try:
        # 将扩展模型转回基础的 UserInput 构建上下文
        base_user = UserInput(**request.model_dump(exclude={"dimension"}))
        context = context_builder.build_context(base_user)
        result = fortune_agent.predict_scores(context, dimension=request.dimension)
        return {"result": result}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/analyze/stream")
async def analyze_bazi_sse(request: UserInput):
    """
    运势分析接口 - 流式方式
    """
    try:
        context = context_builder.build_context(request)
        return StreamingResponse(agent.stream_report(context), media_type="text/plain")
    except Exception as e:
        return StreamingResponse(iter([f"流处理错误: {str(e)}"]), media_type="text/plain")

class GetScoreRequest(BaseModel):
    dimension: str  # 仅支持“流日”
@app.post("/get_fortune_score")
async def get_fortune_score_api(req: GetScoreRequest):
    try:
        return get_fortune_score(req.dimension)
    except OwnerConfigNotFound:
        return JSONResponse(status_code=400, content={"error": "OWNER_CONFIG_NOT_FOUND", "message": "未找到命主配置，请先配置后重试"})
    except ValueError as ve:
        return JSONResponse(status_code=400, content={"error": str(ve)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# 新增：读取当前命主配置（owner.yaml）
@app.get("/owner_config")
def get_owner_config():
    try:
        cfg = load_owner_user_input()
        return {"config": cfg}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# 新增：保存命主配置（owner.yaml）
@app.post("/owner_config")
async def set_owner_config(data: dict):
    try:
        save_owner_user_input(data)
        return {"ok": True}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# 新增：把用户输入转换为四柱（命宫配置用）
@app.post("/calc_bazi")
async def calc_bazi(req: UserInput):
    try:
        ctx = context_builder.build_context(req)
        # ctx.bazi 形如：“辛巳 庚子 辛酉 乙未”
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
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
