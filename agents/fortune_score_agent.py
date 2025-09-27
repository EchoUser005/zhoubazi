import os
from datetime import date
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel
import jinja2
import json

from schemas import BaziContext
from utils.prompt_utils import load_prompt_split
from utils.llm_router import LLMRouter

# 加载环境变量（支持 GEMINI_API_KEY / GOOGLE_API_KEY）
load_dotenv()


class FortuneResult(BaseModel):
    emotion: int
    health: int
    wealth: int


class FortuneScoreAgent:
    """
    运势预测打分 Agent
    - 读取 prompt/predict_fortune.md
    - 使用 LLMRouter 调用 Gemini Flash（gemini-2.5-flash）
    - 由调用方显式传入 dimension，其余模板变量由内部处理
    - 仅当 dimension == '流日' 时，other_info 注入"流日干支：{X}日"，否则为空
    """
    def __init__(
        self,
        prompt_path: Optional[str] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.2,
        timeout: int = 600,
        max_retries: int = 3,
    ):
        # 模板路径
        if prompt_path and os.path.exists(prompt_path):
            self.prompt_path = prompt_path
        else:
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.prompt_path = os.path.join(project_root, "prompt", "predict_fortune.md")

        # 使用统一路由（默认 gemini-2.5-flash）
        self.router = LLMRouter(
            provider=provider or os.getenv("LLM_PROVIDER", "gemini"),
            model=model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            temperature=temperature,
            timeout=timeout,
            max_retries=max_retries,
        )

    def _render_messages(self, context: BaziContext, dimension: str) -> list[tuple[str, str]]:
        """
        读取并渲染 predict_fortune.md：
        - 使用 utils.prompt_utils.load_prompt_split 以 '---' 切分为 system / user
        - 用 Jinja2 分别渲染后返回标准消息列表
        """
        system_tmpl, user_tmpl = load_prompt_split(self.prompt_path)
        sys_template = jinja2.Template(system_tmpl)
        user_template = jinja2.Template(user_tmpl)

        # only 流日 才注入流日干支
        other_info = ""
        if dimension.strip() == "流日":
            from datetime import datetime
            try:
                from zoneinfo import ZoneInfo
                tz = ZoneInfo("Asia/Shanghai")
                now_dt = datetime.now(tz)
            except Exception:
                now_dt = datetime.now()

            from utils.cal_tools import BaziEngine
            try:
                ganzhi = BaziEngine().get_ganzhi_info(now_dt)
                day_ganzhi = (ganzhi or {}).get("day_ganzhi", "")
                other_info = f"流日干支：{day_ganzhi}日" if day_ganzhi else ""
            except Exception:
                other_info = ""

        system_text = sys_template.render(**context.model_dump())
        user_text = user_template.render(
            dimension=dimension,
            other_info=other_info,
            **context.model_dump(),
        )
        return [("system", system_text), ("human", user_text)]

    def predict_scores(self, context: BaziContext, dimension: str) -> dict:
        """
        同步获取结构化打分结果（返回 dict: {emotion, health, wealth}，均为整数）
        """
        messages = self._render_messages(context, dimension)
        text = self.router.invoke(messages)

        if not text or not text.strip():
            # 明确抛出空响应错误，便于调用方感知
            raise ValueError("LLM_EMPTY_RESPONSE")

        # 解析并校验为结构化结果
        try:
            parsed = FortuneResult.model_validate_json(text)  # pydantic v2
        except Exception:
            import re
            # 容错：从输出中提取首个 JSON 对象
            m = re.search(r"\{[\s\S]*\}", text)
            if not m:
                raise ValueError("LLM_JSON_NOT_FOUND")
            data = json.loads(m.group(0))

            def to_int(v):
                if isinstance(v, (int, float)):
                    return max(0, min(100, int(v)))
                if isinstance(v, str):
                    m2 = re.search(r"-?\d+", v)
                    if m2:
                        return max(0, min(100, int(m2.group(0))))
                raise ValueError("INVALID_SCORE_VALUE")

            parsed = FortuneResult(
                emotion=to_int(data.get("emotion")),
                health=to_int(data.get("health")),
                wealth=to_int(data.get("wealth")),
            )
        return parsed.model_dump()