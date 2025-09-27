import os
from typing import Optional, Dict, Any
import yaml

def _project_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _config_path() -> str:
    return os.path.join(_project_root(), "config", "owner.yaml")

def load_owner_user_input() -> Optional[Dict[str, Any]]:
    """
    从 config/owner.yaml 读取命主配置（与 schemas.UserInput 字段一致）
    """
    path = _config_path()
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data

def save_owner_user_input(data: Dict[str, Any]) -> None:
    """
    保存命主配置到 config/owner.yaml（YAML 标准）
    """
    cfg_dir = os.path.dirname(_config_path())
    os.makedirs(cfg_dir, exist_ok=True)
    with open(_config_path(), "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)