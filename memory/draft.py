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
    draft: List[Dict[str, Any]]  # 用于存储报告的草稿
    village_name: str  # 村庄名称
    documents_path: str  # 本地文件的路径
    document: Dict[str, str]  # 本地文件的解析结果
    local_condition: Dict[str, Dict[str, str]]  # 区位分析结果
    '''
    区位分析示例：
    {
        "natural": {
            "海拔高度": "描述",
            "湖泊分布": "描述",
            # 其他自然条件
        },
        "policy": {
            "推进城乡融合发展，构建城乡统一的建设用地市场，推动人才、技术等要素向乡村流动": "描述",
            "细化村庄分类标准，科学确定发展目标": "描述",
            # 其他政策条件
        }
    }
    '''
    model: str  # 使用的模型名称
    navigate: Dict[str, List[str]]  # 导航信息
    '''
    导航信息示例：
    {
        '生态乡村旅游': ['市场空白：...', '成功案例：...', '幸存者偏差：...', '风险：...'],
        '有机生态农业': ['市场空白：...', '成功案例：...', '幸存者偏差：...', '风险：...'],
        ...
    }
    '''
    navigate_analysis: list
