from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any, List

from schemas import UserInput, BaziContext, AnalysisContext
from prompt.context_builder import BaziContextBuilder
from agentic_analyse import LLM_Chat, prompt_template

"""
1. 定义接口，接收原始用户输入的参数模型UserInput 
2. 定义输出，直接返回AI分析结果文本
3. 运行逻辑，
    1. 接收用户输入的参数
    2. 调用context_builder.py中的build_context方法，生成BaziContext
    3. 调用agentic_analyse.py中的ai_chat方法，生成分析结果
    4. 直接返回AI生成的分析文本
"""

# 创建FastAPI应用
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

# 根路由
@app.get("/")
def read_root():
    return {"message": "周运势分析API", "version": "1.0.0"}

# 同步分析接口 - 返回完整分析结果
@app.post("/analyze")
async def analyze_bazi(request: UserInput):
    """
    运势分析接口 - 同步方式
    
    接收用户输入信息，直接返回AI分析结果文本
    """
    try:
        # 1. 构建运势上下文
        builder = BaziContextBuilder()
        bazi_context = builder.build_context(request)
        
        # 2. 分析运势 - 调用LLM进行分析
        llm_chat = LLM_Chat()
        analysis_text = llm_chat.ai_chat(bazi_context)
        
        # 3. 直接返回分析文本
        return analysis_text
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"分析过程出错: {str(e)}"}
        )

# 流式分析接口 - 直接返回分析文本流
async def analyze_bazi_stream(request: UserInput):
    """流式分析过程，直接返回AI生成的文本流"""
    try:
        # 1. 构建上下文
        builder = BaziContextBuilder()
        context = builder.build_context(request)
        
        # 2. 创建LLM实例并进行流式分析
        llm_chat = LLM_Chat()
        
        # 使用自定义流式输出
        stream = llm_chat.llm.stream([
            ("system", prompt_template.format(
                nowtime=context.nowtime,
                calendar=context.calendar,
                name=context.name,
                gender=context.gender,
                isTai=context.isTai,
                birth_correct=context.birth_correct,
                city=context.city,
                bazi=context.bazi,
                dayun_time=context.dayun_time,
                jiaoyun_time=context.jiaoyun_time
            )),
            ("human", "请按照规则所示格式输出分析报告，不要输出任何无关字符")
        ])
        
        # 直接返回流式文本
        for chunk in stream:
            content = ""
            if hasattr(chunk, 'content'):
                content = chunk.content
            else:
                content = str(chunk)
                
            if content:
                yield content
        
    except Exception as e:
        yield f"分析过程出错: {str(e)}"

@app.post("/analyze/stream")
async def analyze_bazi_sse(request: UserInput):
    """
    运势分析接口 - 流式方式
    
    接收用户输入信息，直接返回AI生成的文本流
    """
    return StreamingResponse(
        analyze_bazi_stream(request),
        media_type="text/plain"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
