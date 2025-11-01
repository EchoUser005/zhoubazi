from typing import Iterator, List, Tuple, Union, Optional, AsyncIterator
import os
import logging
from concurrent.futures import ThreadPoolExecutor
from langchain_deepseek import ChatDeepSeek
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()

# 导入配置管理器
try:
    from utils.settings_manager import get_api_key
    HAS_SETTINGS_MANAGER = True
except ImportError:
    HAS_SETTINGS_MANAGER = False
    logger.warning("settings_manager not found, using env vars only")

Message = Tuple[str, str]
Messages = List[Message]


_executor = ThreadPoolExecutor(max_workers=4)


class LLMRouter:

    def __init__(
            self,
            provider: str | None = None,
            model: str | None = None,
            temperature: float = 0.5,
            timeout: int | None = 600,
            max_retries: int = 3,
    ) -> None:
        self.provider = (provider or os.getenv("LLM_PROVIDER", "deepseek")).lower()
        self.temperature = temperature
        self.timeout = timeout
        self.max_retries = max_retries

        # 从配置文件获取 API key（优先级高于环境变量）
        if HAS_SETTINGS_MANAGER:
            if self.provider == "deepseek":
                api_key = get_api_key("deepseek")
                if api_key:
                    os.environ["DEEPSEEK_API_KEY"] = api_key
            elif self.provider == "gemini":
                api_key = get_api_key("gemini")
                if api_key:
                    os.environ["GEMINI_API_KEY"] = api_key
                    os.environ["GOOGLE_API_KEY"] = api_key  # langchain 可能用这个

        if self.provider == "deepseek":
            self.model = model or os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
            self.llm = ChatDeepSeek(
                model=self.model,
                temperature=self.temperature,
                max_tokens=None,
                timeout=self.timeout,
                max_retries=self.max_retries,
            )
        elif self.provider == "gemini":
            self.model = model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
            self.llm = ChatGoogleGenerativeAI(
                model=self.model,
                temperature=self.temperature,
                max_tokens=None,
                timeout=self.timeout,
                max_retries=self.max_retries,
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

        print(f"[LLMRouter] Initialized with provider={self.provider}, model={self.model}")

    def invoke(self, messages: Union[str, Messages]) -> str:
        """同步调用（保持不变）"""
        msgs = self._normalize_messages(messages)
        result = self.llm.invoke(msgs)
        return getattr(result, "content", str(result))

    def stream(self, messages):
        msgs = self._normalize_messages(messages)
        logger.info(f"[stream] model={self.model}")
        for chunk in self.llm.stream(msgs):
            logger.debug(f"[stream] chunk type: {type(chunk)}, content: {str(chunk)[:100]}")
            if hasattr(chunk, "content") and isinstance(chunk.content, str):
                yield chunk.content

    def invoke_reasoning(self, messages: Union[str, Messages]) -> dict:
        """思考模型调用（保持不变）"""
        msgs = self._normalize_messages(messages)

        if self.provider == "deepseek":
            model = os.getenv("DEEPSEEK_REASONING_MODEL", "deepseek-reasoner")
            ds = ChatDeepSeek(
                model=model,
                temperature=self.temperature,
                max_tokens=None,
                timeout=self.timeout,
                max_retries=self.max_retries,
            )
            ai_msg = ds.invoke(msgs)
            reasoning = None
            if hasattr(ai_msg, "additional_kwargs") and isinstance(ai_msg.additional_kwargs, dict):
                reasoning = ai_msg.additional_kwargs.get("reasoning_content")
            content = getattr(ai_msg, "content", "") or ""
            return {"reasoning": reasoning, "content": content}

        elif self.provider == "gemini":
            try:
                from google import genai
                from google.genai import types
                api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
                if not api_key:
                    raise ValueError("缺少 GEMINI_API_KEY/GOOGLE_API_KEY 环境变量")
                client = genai.Client(api_key=api_key)

                prompt = self._join_as_prompt(msgs)
                resp = client.models.generate_content(
                    model=os.getenv("GEMINI_REASONING_MODEL", "gemini-2.5-pro"),
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        thinking_config=types.ThinkingConfig(include_thoughts=True)
                    ),
                )

                reasoning: Optional[str] = None
                content_parts: List[str] = []
                cand = resp.candidates[0] if resp.candidates else None
                if cand and cand.content and getattr(cand.content, "parts", None):
                    parts = getattr(cand.content, "parts", [])
                    for part in parts:
                        if getattr(part, "thought", False) and getattr(part, "text", None):
                            part_text = getattr(part, "text", "")
                            if part_text:
                                reasoning = (reasoning or "") + part_text
                        elif getattr(part, "text", None):
                            part_text = getattr(part, "text", "")
                            if part_text:
                                content_parts.append(part_text)
                return {"reasoning": reasoning, "content": "".join(content_parts) if content_parts else ""}

            except Exception:
                ai_msg = self.llm.invoke(msgs)
                return {"reasoning": None, "content": getattr(ai_msg, "content", "") or ""}

        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

    @staticmethod
    def build_messages(system: str | None, user: str) -> Messages:
        msgs: Messages = []
        if system:
            msgs.append(("system", system))
        msgs.append(("human", user))
        return msgs

    @staticmethod
    def _normalize_messages(messages: Union[str, Messages]) -> Messages:
        if isinstance(messages, str):
            return [("human", messages)]
        if not isinstance(messages, list) or not all(
                isinstance(m, tuple) and len(m) == 2 for m in messages
        ):
            raise TypeError("messages 必须为字符串或 [('role','content'), ...] 列表")
        return messages

    @staticmethod
    def _join_as_prompt(messages: Messages) -> str:
        sys_parts = [t for r, t in messages if r == "system"]
        other_parts = [t for r, t in messages if r != "system"]
        blocks = []
        if sys_parts:
            blocks.append(sys_parts[0])
        if other_parts:
            blocks.append("\n---\n".join(other_parts))
        return "\n\n---\n\n".join(blocks) if blocks else ""

