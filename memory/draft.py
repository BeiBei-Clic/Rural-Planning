from typing import TypedDict, List, Dict, Any


# 定义 rural_DraftState
class rural_DraftState(TypedDict):
    draft: List[Dict[str, Any]]  # 每个版本的内容存储为字典
    Village_name: str
    Documents_path: str
    Document: dict
    Local_Conditions:dict
    model: str
