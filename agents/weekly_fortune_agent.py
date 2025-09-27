import os
import logging
from typing import Iterator, Optional
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate

from schemas import BaziContext
from utils.llm_router import LLMRouter
from utils.tracing import trace_agent_action

load_dotenv()
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s - %(levelname)s - %(message)s",
)

try:
    with open("prompt/system_prompt.txt", "r", encoding="utf-8") as f:
        _template_string = f.read()
except FileNotFoundError:
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    prompt_path = os.path.join(current_dir, "prompt", "system_prompt.txt")
    with open(prompt_path, "r", encoding="utf-8") as f:
        _template_string = f.read()

prompt_template = PromptTemplate.from_template(_template_string)


class WeeklyFortuneAgent:
    """
    周运势分析 Agent
    - 封装了与 LLM 的交互（同步/流式）
    - 通过 LLMRouter 统一管理 Gemini / DeepSeek
    """

    def __init__(
        self,
        router: Optional[LLMRouter] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.5,
        timeout: int = 600,
        max_retries: int = 3,
    ):
        # 允许从外部注入 router，便于测试；否则按全局配置创建
        self.router = router or LLMRouter(
            provider=provider or os.getenv("LLM_PROVIDER", "gemini"),
            model=model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            temperature=temperature,
            timeout=timeout,
            max_retries=max_retries,
        )

    def _build_messages(self, context: BaziContext) -> list[tuple[str, str]]:
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
            qiyun_time=getattr(context, "qiyun_time", ""),  # 兜底，避免 KeyError
            jiaoyun_time=context.jiaoyun_time,
        )
        user_message = "请严格按照规则所示的输出格式生成分析报告，不要输出任何无关字符"
        return [("system", system_message), ("human", user_message)]

    # 同步整段输出
    @trace_agent_action(name="generate_fortune_report", agent_type="weekly_fortune")
    def generate_report(self, context: BaziContext) -> str:
        messages = self._build_messages(context)
        return self.router.invoke(messages)

    # 流式输出（生成器）
    @trace_agent_action(name="stream_fortune_report", agent_type="weekly_fortune")
    def stream_report(self, context: BaziContext) -> Iterator[str]:
        messages = self._build_messages(context)
        return self.router.stream(messages)