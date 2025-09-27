from typing import Iterator, List, Tuple, Union, Optional
import os

from langchain_deepseek import ChatDeepSeek
from langchain_google_genai import ChatGoogleGenerativeAI

Message = Tuple[str, str]
Messages = List[Message]

class LLMRouter:
    """
    简洁的 LLM 路由器：
    - 统一对外接口 invoke / stream / invoke_reasoning
    - 内部选择 deepseek 或 gemini
    - 入参支持:
        - 纯字符串 -> 自动包装为 [("human", text)]
        - LangChain 消息列表: [("system", ...), ("human", ...)]
    环境变量：
        LLM_PROVIDER=deepseek|gemini
        DEEPSEEK_MODEL=deepseek-chat （可选，常规）
        DEEPSEEK_REASONING_MODEL=deepseek-reasoner （可选，思考）
        GEMINI_MODEL=gemini-2.5-flash （可选，常规）
        GEMINI_REASONING_MODEL=gemini-2.5-pro （可选，思考）
        GOOGLE_API_KEY / GEMINI_API_KEY（二选一，Gemini官方客户端）
        DEEPSEEK_API_KEY（DeepSeek）
    """
    def __init__(
        self,
        provider: str | None = None,  # deepseek|gemini
        model: str | None = None,  # deepseek-chat|gemini-2.5-flash
        temperature: float = 0.5,
        timeout: int | None = 600,
        max_retries: int = 3,
    ) -> None:
        self.provider = (provider or os.getenv("LLM_PROVIDER", "deepseek")).lower()
        self.temperature = temperature
        self.timeout = timeout
        self.max_retries = max_retries

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


    def invoke(self, messages: Union[str, Messages]) -> str:
        msgs = self._normalize_messages(messages)
        result = self.llm.invoke(msgs)
        return getattr(result, "content", str(result))


    def stream(self, messages: Union[str, Messages]) -> Iterator[str]:
        msgs = self._normalize_messages(messages)
        for chunk in self.llm.stream(msgs):
            if hasattr(chunk, "content") and isinstance(chunk.content, str):
                yield chunk.content

    # 新增：思考模型调用，返回 reasoning + content
    def invoke_reasoning(self, messages: Union[str, Messages]) -> dict:
        """
        调用“思考模型”，返回：
        {
            "reasoning": Optional[str],  # 推理过程
            "content": str               # 最终答案
        }
        - deepseek 使用 deepseek-reasoner，reasoning 从 additional_kwargs['reasoning_content'] 读取
        - gemini 使用 gemini-2.5-pro，并启用 include_thoughts，从 thought 与非 thought 的 parts 中分别抽取
        """
        msgs = self._normalize_messages(messages)

        if self.provider == "deepseek":
            # 单独实例化 R1（思考模型）
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
            # 使用官方 google.genai 客户端开启 include_thoughts
            try:
                from google import genai
                from google.genai import types  # 为 thinking_config 提供类型
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
                        # 思考内容
                        if getattr(part, "thought", False) and getattr(part, "text", None):
                            part_text = getattr(part, "text", "")
                            if part_text:
                                reasoning = (reasoning or "") + part_text
                        # 最终输出
                        elif getattr(part, "text", None):
                            part_text = getattr(part, "text", "")
                            if part_text:
                                content_parts.append(part_text)
                return {"reasoning": reasoning, "content": "".join(content_parts) if content_parts else ""}

            except Exception:
                # 回退到 LangChain 的常规调用（没有 thoughts，只返回 content）
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
        """
        把 system/human/assistant 合并为一个纯文本 prompt，便于丢给官方 SDK。
        约定：优先拼接首个 system，再拼接其余 human/assistant，使用分隔符分开，避免语义混淆。
        """
        sys_parts = [t for r, t in messages if r == "system"]
        other_parts = [t for r, t in messages if r != "system"]
        blocks = []
        if sys_parts:
            blocks.append(sys_parts[0])
        if other_parts:
            blocks.append("\n---\n".join(other_parts))
        return "\n\n---\n\n".join(blocks) if blocks else ""