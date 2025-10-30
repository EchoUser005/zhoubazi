import logging
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from schemas import BaziContext
from prompt.context_builder import BaziContextBuilder
from utils.llm_router import LLMRouter
from utils.prompt_utils import mk_single_turn_messages
import os

load_dotenv()

logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO').upper(), format='%(asctime)s - %(levelname)s - %(message)s')



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

        self.router = LLMRouter(
            provider=os.getenv("LLM_PROVIDER", "deepseek"),# gemini deepseek
            model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),# gemini-2.5-flash deepseek-chat
            temperature=0.5,
            timeout=600,
            max_retries=3,
        )

    def stream_chat(self, context: BaziContext):
        """
        [流式] 使用 LLM 生成运势分析报告, 返回一个可迭代的文本流。
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
            qiyun_time=getattr(context, "qiyun_time", ""),
            jiaoyun_time=context.jiaoyun_time
        )

        user_message = "请严格按照规则所示的输出格式生成分析报告，不要输出任何无关字符"
        messages = [
            ("system", system_message),
            ("human", user_message),
        ]

        # 返回底层路由器的流，供调用方 for chunk in ... 消费
        return self.router.stream(messages)

    def get_full_response(self, context: BaziContext) -> str:
        """
        [同步] 使用 LLM 生成完整的运势分析报告，返回整段文本。
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
            qiyun_time=getattr(context, "qiyun_time", ""),
            jiaoyun_time=context.jiaoyun_time
        )

        user_message = "请严格按照规则所示的输出格式生成分析报告，不要输出任何无关字符"
        messages = [
            ("system", system_message),
            ("human", user_message),
        ]
        return self.router.invoke(messages)


if __name__ == "__main__":
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