import logging
from langchain_deepseek import ChatDeepSeek
import os
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from schemas import BaziContext 
from prompt.context_builder import BaziContextBuilder
from schemas import UserInput

# Load environment variables from a .env file at the very top
load_dotenv()

logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO').upper(), format='%(asctime)s - %(levelname)s - %(message)s')

# Check for API key after loading .env. If not found, raise a clear error.
if not os.getenv("DEEPSEEK_API_KEY"):
    raise ValueError(
        "错误: DEEPSEEK_API_KEY 未在环境变量中设置。\n"
        "请遵循以下步骤:\n"
        "1. 在项目根目录中, 将 .env.example 文件复制一份并重命名为 .env\n"
        "2. 打开 .env 文件, 将 'YOUR_DEEPSEEK_API_KEY_HERE' 替换为您的有效API密钥。"
    )


try:

    with open("prompt/system_prompt.txt", "r", encoding="utf-8") as f:
        template_string = f.read()
except FileNotFoundError:

    current_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.join(current_dir, "prompt", "system_prompt.txt")
    with open(prompt_path, "r", encoding="utf-8") as f:
        template_string = f.read()


prompt_template = PromptTemplate.from_template(template_string)

__all__ = ["LLM_Chat", "prompt_template"]

class LLM_Chat:
    def __init__(self):
        self.llm = ChatDeepSeek(
            model="deepseek-chat",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2
        )

    def stream_chat(self, context: BaziContext):
        """
        [流式] 使用LLM生成运势分析报告.
        这是一个生成器函数，会流式返回AI的响应块。
        """
        system_message = prompt_template.format(
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
        )
        
        logging.debug(system_message)

        user_prompt = "请按照规则所示格式输出分析报告，不要输出任何无关字符"
        
        messages = [
            ("system", system_message),
            ("human", user_prompt),
        ]
        
        stream = self.llm.stream(messages)
        
        for chunk in stream:
            if hasattr(chunk, 'content') and isinstance(chunk.content, str):
                yield chunk.content

    def get_full_response(self, context: BaziContext) -> str:
        """
        [同步] 使用LLM生成完整的运势分析报告.
        """
        full_response = "".join(self.stream_chat(context))
        return full_response


if __name__ == "__main__":
    import sys
    from schemas import UserInput
    
    test_user = UserInput(
        birth_time="2001-12-23 13:00:00",
        birth_location="浙江省金华市东阳市",
        name="测试用户",
        gender="女",
        isTai=False,
        city="北京",
        is_lunar=False
    )
    
    context_builder = BaziContextBuilder()
    llm_chat = LLM_Chat()
    
    try:
        context = context_builder.build_context(test_user)
        
        print("\n" + "="*50)
        print("☯ 五行运势周报 (流式测试)")
        print("="*50)
        
        # 测试流式功能
        for chunk in llm_chat.stream_chat(context):
            print(chunk, end="", flush=True)
        
        print("\n\n" + "="*50)
        print("☯ 五行运势周报 (同步测试)")
        print("="*50)

        # 测试同步功能
        full_text = llm_chat.get_full_response(context)
        print(full_text)

        print("\n" + "="*50)
        
    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()