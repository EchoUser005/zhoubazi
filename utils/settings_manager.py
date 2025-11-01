"""
配置管理模块
支持动态读取和保存 API keys 等配置信息
"""
import os
import yaml
from pathlib import Path
from typing import Optional

SETTINGS_FILE = Path(__file__).parent.parent / "config" / "settings.yaml"


def load_settings() -> dict:
    """读取配置文件"""
    if not SETTINGS_FILE.exists():
        # 如果文件不存在，返回默认配置
        return {
            "gemini_api_key": os.getenv("GEMINI_API_KEY", ""),
            "deepseek_api_key": os.getenv("DEEPSEEK_API_KEY", ""),
            "llm_provider": os.getenv("LLM_PROVIDER", "gemini"),
        }

    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
        settings = yaml.safe_load(f) or {}

    # 如果配置文件中没有，尝试从环境变量读取
    settings.setdefault("gemini_api_key", os.getenv("GEMINI_API_KEY", ""))
    settings.setdefault("deepseek_api_key", os.getenv("DEEPSEEK_API_KEY", ""))
    settings.setdefault("llm_provider", os.getenv("LLM_PROVIDER", "gemini"))

    return settings


def save_settings(settings: dict) -> None:
    """保存配置文件"""
    # 确保配置目录存在
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        yaml.safe_dump(settings, f, allow_unicode=True, default_flow_style=False)


def get_api_key(provider: str) -> Optional[str]:
    """获取指定 provider 的 API key"""
    settings = load_settings()

    if provider == "gemini":
        return settings.get("gemini_api_key") or os.getenv("GEMINI_API_KEY")
    elif provider == "deepseek":
        return settings.get("deepseek_api_key") or os.getenv("DEEPSEEK_API_KEY")

    return None


def update_api_key(provider: str, api_key: str) -> None:
    """更新指定 provider 的 API key"""
    settings = load_settings()

    if provider == "gemini":
        settings["gemini_api_key"] = api_key
    elif provider == "deepseek":
        settings["deepseek_api_key"] = api_key

    save_settings(settings)
