from google import genai
# from google.genai import types
from dotenv import load_dotenv
import os
import sys
from pydantic import BaseModel

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from schemas import BaziContext
from langchain_google_genai import ChatGoogleGenerativeAI
from utils.prompt_utils import load_prompt, load_prompt_split



# 定义输出结构
class FortuneResult(BaseModel):
    emotion: int
    health: int
    wealth: int

# 加载环境变量
load_dotenv()

def gemini_chat_nostream(prompt: str) -> FortuneResult:
    """
    使用gemini-2.5-flash模型获取结构化输出
    """
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": FortuneResult,
        },
    )
    
    # 返回解析后的对象
    content = response.parsed
    return content


def gemini_chat_reasoning(prompt: str) -> FortuneResult:

    response = client.models.generate_content(
        model="gemini-2.5-pro",
        contents=prompt,

        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(
                include_thoughts=True
                )
            )
    )


    for part in response.candidates[0].content.parts:
        if not part.text:
            continue
        if part.thought:
            print("reasoning:")
            reasoning = part.text
            print(reasoning)


        else:
            print("content:")
            content = part.text
            print(content)
    
    return reasoning, content


if __name__ == "__main__":
    import jinja2

    mock_context = BaziContext(
        nowtime="乙巳年甲申月",
        calendar="周一 己未日 8月18日\\n周二 庚申日 8月19日...",
        name="模拟用户",
        gender="女",
        isTai="否",
        birth_correct="公历 2001年12月23日 13:00 辛巳年 庚子月 辛酉日 乙未时",
        city="北京",
        bazi="辛巳 庚子 辛酉 乙未",
        dayun_time="8岁 2009年 辛丑 -> 18岁 2019年 壬寅 -> ...",
        qiyun_time="出生后7年10月15日 上大运",
        jiaoyun_time="逢丙、辛年 11月8日交大运"
    )

    prompt_path = rf"/Users/m4pro/Documents/llm/zhoubazi/prompt/predict_fortune.md"
    prompt_loaded = load_prompt(prompt_path)

    prompt = jinja2.Template(prompt_loaded).render(
        dimension="流月",
        other_info="",
        **mock_context.model_dump()
    )
    print(f"填充后 prompt 是: {prompt}")
    # prompt_test = "你是谁"
    content = gemini_chat_nostream(prompt)
    print(content)


# 测试思考模型
# client = genai.Client()

# llm = ChatGoogleGenerativeAI(
#     model="gemini-2.5-pro",  
#     temperature=0.2,
# )
# print(llm.invoke("ddd 收到回复 1").content)

