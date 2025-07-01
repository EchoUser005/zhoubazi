import os
import uvicorn
from fastapi import FastAPI
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from schemas import UserInput
from prompt.context_builder import BaziContextBuilder
from agentic_analyse import LLM_Chat

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


llm_chat = LLM_Chat()
context_builder = BaziContextBuilder()


@app.get("/")
def read_root():
    return {"message": "周运势分析API", "version": "1.0.0"}

@app.post("/analyze")
async def analyze_bazi(request: UserInput):
    """
    运势分析接口 - 同步方式
    """
    try:
        context = context_builder.build_context(request)
        analysis_text = llm_chat.get_full_response(context)
        return {"result": analysis_text}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"分析过程出错: {str(e)}"})

@app.post("/analyze/stream")
async def analyze_bazi_sse(request: UserInput):
    """
    运势分析接口 - 流式方式
    """
    try:
        context = context_builder.build_context(request)
        return StreamingResponse(llm_chat.stream_chat(context), media_type="text/plain")
    except Exception as e:
        print(f"流式分析出错: {e}")
        return StreamingResponse(iter([f"流处理错误: {str(e)}"]), media_type="text/plain")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
