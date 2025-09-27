"""
- 对外唯一入口：get_fortune_score(dimension: str) -> dict
- 目前只支持维度：'流日'
- 评分唯一键：YYYY-MM-DD（Asia/Shanghai）
- 未做任何“自然触发”，仅在调用时执行“查库或预测再写库”
"""
from __future__ import annotations

from datetime import datetime
from typing import Dict, Any

from prompt.context_builder import BaziContextBuilder
from agents.fortune_score_agent import FortuneScoreAgent
from schemas import UserInput
from utils.config_loader import load_owner_user_input
from db.db_manager import db as scores_repo


class OwnerConfigNotFound(Exception):
    """命主配置缺失异常：需要先配置 config/owner.yaml"""
    pass


# 单例式依赖，避免每次调用重复初始化
_context_builder = BaziContextBuilder()
_fortune_agent = FortuneScoreAgent()


def _today_key() -> str:
    """
    返回今日的 key：YYYY-MM-DD
    优先使用 Asia/Shanghai；若不可用则回退本地时间
    """
    try:
        from zoneinfo import ZoneInfo
        tz = ZoneInfo("Asia/Shanghai")
        return datetime.now(tz).strftime("%Y-%m-%d")
    except Exception:
        return datetime.now().strftime("%Y-%m-%d")


def get_fortune_score(dimension: str) -> Dict[str, Any]:
    """
    应用服务入口：获取三维评分（情感/健康/财富）
    - 先查评分库，命中直接返回（source=db）
    - 未命中则读取命主配置 → 构建上下文 → 调用算法 → 入库 → 返回（source=model）

    入参：
        dimension: 仅支持 '流日'
    返回：
        {
          "result": {"emotion": int, "health": int, "wealth": int},
          "source": "db" | "model",
          "key": "YYYY-MM-DD"
        }
    异常：
        ValueError: 维度非法
        OwnerConfigNotFound: 未配置命主（config/owner.yaml）
        其他异常：向上抛出交由路由层统一处理
    """
    dim = (dimension or "").strip()
    if dim != "流日":
        raise ValueError("仅支持维度：流日")

    key = _today_key()

    # 1) 查库命中
    hit = scores_repo.get_score(dimension=dim, key=key)
    if hit:
        return {
            "result": {
                "emotion": hit["emotion"],
                "health": hit["health"],
                "wealth": hit["wealth"],
            },
            "source": "db",
            "key": key,
        }

    # 2) 未命中 → 读取命主配置
    owner_cfg = load_owner_user_input()
    if not owner_cfg:
        # 交由路由层返回 400 + 友好消息
        raise OwnerConfigNotFound("OWNER_CONFIG_NOT_FOUND")

    # 3) 构建上下文 → 调用算法（流日干支注入在 Agent 内部处理）
    owner_input = UserInput(**owner_cfg)
    context = _context_builder.build_context(owner_input)
    scores = _fortune_scores(context)

    # 4) 入库并返回
    scores_repo.upsert_score(dimension=dim, key=key, scores=scores, source="model")
    return {"result": scores, "source": "model", "key": key}


def _fortune_scores(context) -> Dict[str, int]:
    """
    内部封装：调用打分 Agent 获取三维分
    注意：流日干支注入在 FortuneScoreAgent 内部 _render_messages 中完成
    """
    # 仅支持流日
    return _fortune_agent.predict_scores(context, dimension="流日")

if __name__ == "__main__":
    # 方便本地快速校验业务逻辑，不依赖 FastAPI
    try:
        print("[ServiceCheck] 调用 get_fortune_score('流日') ...")
        result = get_fortune_score("流日")
        print("[ServiceCheck] OK:", result)
    except OwnerConfigNotFound:
        print("[ServiceCheck] 命主配置未找到（config/owner.yaml），请先配置后重试。")
    except ValueError as ve:
        print("[ServiceCheck] 参数错误：", ve)
    except Exception as e:
        print("[ServiceCheck] 未预期错误：", e)