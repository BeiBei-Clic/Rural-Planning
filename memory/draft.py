from typing import TypedDict, List, Dict, Any


# 定义 rural_DraftState
class rural_DraftState(TypedDict):
    """
    用于存储乡村振兴规划报告的草稿及相关信息。

    :param draft: 报告的草稿列表
    :param village_name: 村庄名称
    :param documents_path: 本地文件的路径
    :param document: 本地文件的解析结果
    :param local_condition: 区位分析结果
    :param model: 使用的模型名称
    :param navigate: 导航信息
    """
    village_name: str  # 村庄名称
    documents_path: str  # 本地文件的路径
    document: Dict[str, str]  # 本地文件的解析结果
    model: str  # 使用的模型名称
    development_plan: Dict[str, Any]  # 发展规划结果
    review: Dict[str, Any]  # 审核结果
    passed: str  # 审核结果
