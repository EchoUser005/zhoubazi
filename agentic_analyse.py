from langchain_deepseek import ChatDeepSeek
import os
import getpass
from langchain_core.prompts import PromptTemplate
from schemas import BaziContext  # 导入BaziContext模型用于类型校验
from prompt.context_builder import BaziContextBuilder
from schemas import UserInput


# 加载API密钥
if not os.getenv("DEEPSEEK_API_KEY"):
    os.environ["DEEPSEEK_API_KEY"] = getpass.getpass("输入你的DeepSeek API key: ")

# 从文件读取系统提示模板
try:
    # 尝试使用相对路径
    with open("prompt/system_prompt.txt", "r", encoding="utf-8") as f:
        template_string = f.read()
except FileNotFoundError:
    # 如果失败，尝试使用绝对路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.join(current_dir, "prompt", "system_prompt.txt")
    with open(prompt_path, "r", encoding="utf-8") as f:
        template_string = f.read()

# 创建提示模板
prompt_template = PromptTemplate.from_template(template_string)

# 导出prompt_template变量，以便在main.py中使用
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

    def ai_chat(self, context: BaziContext, stream_output=False):
        """
        使用LLM生成运势分析报告
        
        Args:
            context: 排盘上下文信息
            stream_output: 是否流式输出，如果为True则实时打印响应
            
        Returns:
            生成的完整响应文本
        """
        # 使用提示模板格式化系统消息
        system_message = prompt_template.format(
            nowtime=context.nowtime,
            calendar=context.calendar,
            name=context.name,
            gender=context.gender,  # 注意这里映射gender到sex
            isTai=context.isTai,
            birth_correct=context.birth_correct,  # 使用已拼接好的birth_correct
            city=context.city,
            bazi=context.bazi,
            dayun_time=context.dayun_time,
            jiaoyun_time=context.jiaoyun_time
        )
        
        # 使用固定的用户提示语，不依赖外部输入
        user_prompt = "请按照规则所示格式输出分析报告，不要输出任何无关字符"
        
        messages = [
            ("system", system_message),
            ("human", user_prompt),
        ]
        
        stream = self.llm.stream(messages)
        full_response = ""
        for chunk in stream:
            # 处理AIMessageChunk对象，提取content
            content = ""
            if hasattr(chunk, 'content'):
                content = chunk.content
            else:
                content = str(chunk)
                
            full_response += content
            
            # 如果启用了流式输出，则实时打印
            if stream_output and content:
                print(content, end="", flush=True)
        
        return full_response


if __name__ == "__main__":
    import sys
    from schemas import UserInput
    
    # 创建测试用户数据
    test_user = UserInput(
        birth_time="2001-12-23 13:00:00",
        birth_location="浙江省金华市东阳市",
        name="测试用户",
        gender="女",
        isTai=False,
        city="北京"
    )
    
    # 创建上下文构建器和LLM聊天对象
    context_builder = BaziContextBuilder()
    llm_chat = LLM_Chat()
    
    # 构建上下文
    try:
        context = context_builder.build_context(test_user)
        
        print("\n" + "="*50)
        print("☯ 五行运势周报")
        print("="*50)
        
        # 测试AI聊天功能，启用流式输出
        response = llm_chat.ai_chat(context, stream_output=True)
        
        print("\n" + "="*50)
        
    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()