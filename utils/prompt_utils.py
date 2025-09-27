from typing import List, Tuple

DEFAULT_DIVIDER = "---"

def join_fragments(fragments: List[str], sep: str = "\n\n") -> str:
    clean = [frag.strip() for frag in fragments if frag and frag.strip()]
    return sep.join(clean)

def mk_single_turn_messages(system: str, user: str | None = None, user_fragments: List[str] | None = None) -> list[tuple[str, str]]:
    """
    生成单轮对话的标准消息列表：[("system", ...), ("human", ...)]
    - 支持直接传 user 字符串，或者用 user_fragments 片段库拼接
    """
    if user is None and user_fragments:
        user = join_fragments(user_fragments)
    if user is None:
        user = ""
    return [("system", system.strip()), ("human", user.strip())]

def split_system_user(combined: str, divider: str = DEFAULT_DIVIDER) -> Tuple[str, str]:
    """
    将“system --- user”合并文本拆分为 (system, user) 两段。
    仅按第一个分隔符切分；如果未找到分隔符，则视为只有 system，无 user。
    """
    if not combined:
        return "", ""
    parts = combined.split(divider, 1)
    if len(parts) == 1:
        return parts[0].strip(), ""
    return parts[0].strip(), parts[1].strip()

def load_prompt_split(prompt_path: str) -> tuple[str, str]:
    with open(prompt_path, 'r', encoding='utf-8') as f:
        prompt_template_str = f.read()
        system_prompt = prompt_template_str.split("---")[0]
        user_prompt = prompt_template_str.split("---")[1] if "---" in prompt_template_str else ""
    return system_prompt, user_prompt