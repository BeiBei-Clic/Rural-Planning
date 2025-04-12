import os
from typing import Dict, Any
import asyncio
from langchain_openai import ChatOpenAI

from memory.draft import rural_DraftState


class ConditionAgent:
    """
    条件分析智能体，用于从 Markdown 文件读取内容并生成自然条件或政策分析报告。
    """

    def __init__(self, draft: rural_DraftState):
        """
        初始化条件分析智能体。

        :param draft: rural_DraftState 实例，包含村庄名称、文件路径等信息
        """
        self.draft = draft

    async def generate_analysis(self, condition_type: str, condition: str) -> Dict[str, Any]:
        """
        生成分析报告。

        :param condition_type: 分析类型，"natural" 表示自然条件分析，"policy" 表示政策分析
        :param condition: 具体的条件名称
        :return: 更新后的 draft_state，包含生成的分析报告
        """
        # 根据分析类型构造提示信息
        if condition_type == "natural":
            prompt = self._construct_natural_analysis_prompt(condition)
        elif condition_type == "policy":
            prompt = self._construct_policy_analysis_prompt(condition)
        else:
            raise ValueError("Invalid analysis type. Use 'natural' or 'policy'.")

        # 调用模型生成分析报告
        response = await ChatOpenAI(model_name=self.draft["model"]).ainvoke([{"role": "user", "content": prompt}])

        # 更新 draft_state，添加新的报告版本
        if condition_type == "natural":
            self.draft["Local_Conditions"]["Natural"][condition] = response.content
        elif condition_type == "policy":
            self.draft["Local_Conditions"]["Policy"][condition] = response.content

        return self.draft

    def _construct_natural_analysis_prompt(self, condition: str) -> str:
        """
        构造自然条件分析的提示信息。

        :param condition: 具体的自然条件名称
        :return: 构造好的提示信息
        """
        return f'''
请根据以下 Markdown 文件内容生成{self.draft["Village_name"]}村的关于{condition}区位分析报告：

{self.draft["Document"]}

**要求**：
- 结合文档分析，但不用完全依赖文档内容，结合你对自然条件的理解和案例分析。
- 先看看{self.draft["Village_name"]}村的{condition}自然条件优劣势，找出具体数字作为支撑。
- 搜寻拥有类似区位条件的村庄的成功和失败案例，分析该村{condition}条件的优劣势，给出具体数字作为支撑。
- 如果是优势，分析该案例村是如何利用的；如果是劣势，分析该案例村是如何克服的。
'''

    def _construct_policy_analysis_prompt(self, condition: str) -> str:
        """
        构造政策分析的提示信息。

        :param condition: 具体的政策条件名称
        :return: 构造好的提示信息
        """
        return f'''
请根据以下 Markdown 文件内容生成{self.draft["Village_name"]}村的关于{condition}区位分析报告：

{self.draft["Document"]}

**要求**：
- 结合文档分析，但不用完全依赖文档内容，结合你对政策的理解和案例分析。
- 先看看{self.draft["Village_name"]}村享受的{condition}政策优劣势，给出具体的文件、数字作为支撑。
- 搜寻拥有类似政策区位的村庄的成功和失败案例，分析该村{condition}条件的优劣势，给出具体文件、数字作为支撑。
- 要找出真实的村庄，不要捏造
- 必须要给出具体的政策文件
- 如果是优势，分析该案例村是如何利用的；如果是劣势，分析该案例村是如何克服的。
'''


def read_markdown_files(directory_path: str) -> Dict[str, str]:
    """
    读取指定路径下的所有 Markdown 文件，并将内容存储在字典中。

    :param directory_path: 包含 Markdown 文件的目录路径
    :return: 一个字典，键是文件名（不包括扩展名），值是文件内容
    """
    markdown_files = {}
    for filename in os.listdir(directory_path):
        if filename.endswith(".md"):
            file_path = os.path.join(directory_path, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
                    markdown_files[os.path.splitext(filename)[0]] = content
            except Exception as e:
                print(f"Error reading file {filename}: {e}")
    return markdown_files


async def main():
    """
    测试条件分析智能体的功能。
    """
    # 创建 rural_DraftState 实例
    draft = rural_DraftState(
        draft=[],
        Village_name="金田村",
        Document=read_markdown_files("Resource"),
        model="glm-4-flash",
        Local_Conditions={"Natural": {}, "Policy": {}},
    )

    # 初始化条件分析智能体
    analysis_agent = ConditionAgent(draft=draft)

    # 定义自然条件因素列表
    natural_factors = [
        "地形地貌", "海拔高度", "坡度", "坡向", "土壤类型", "土壤肥力", "水资源状况", "河流分布", "湖泊分布",
        "地下水位", "气候条件", "气温", "降水", "日照", "风向", "风速", "湿度", "生态敏感度", "植被覆盖度",
        "生物多样性", "自然灾害风险", "地质灾害风险", "气象灾害风险", "水文地质条件", "矿产资源分布", "自然景观资源",
        "森林资源", "草地资源", "湿地资源", "海洋资源", "土地利用现状", "耕地质量", "林地面积", "草地面积", "水域面积",
        "未利用地面积", "土地适宜性", "农业适宜性", "建设用地适宜性", "生态保护红线", "水源保护区", "自然保护区",
        "风景名胜区", "地质公园", "湿地公园", "森林公园", "生态廊道", "生态节点", "交通可达性", "与城市的距离",
        "与主要交通干线的距离", "与周边乡村的连通性", "能源供应条件", "太阳能资源", "风能资源", "水能资源", "地热资源",
        "生物能资源", "环境容量", "大气环境容量", "水环境容量", "土壤环境容量", "生态服务功能", "水源涵养功能",
        "土壤保持功能", "洪水调蓄功能", "生物栖息地功能", "气候调节功能", "废弃物处理能力"
    ]

    # 定义政策条件因素列表
    policy_factors = [
        "推进城乡融合发展，构建城乡统一的建设用地市场，推动人才、技术等要素向乡村流动",
        "细化村庄分类标准，科学确定发展目标",
        "加大高标准农田建设投入，完善建设、验收、管护机制",
        "优化科技创新体系，发展智慧农业",
        "完善粮食生产补贴和保险政策",
        "发展乡村种养业、加工流通业、休闲旅游业等",
        "支持农产品加工产业园和农村电商发展",
        "健全生态保护补偿制度，推进生态综合补偿",
        "提高农村公路、供水、能源等基础设施水平",
        "探索自愿有偿退出办法，保障进城落户农民合法土地权益",
        "推动县域产业协同发展",
        "明确用地类型和供地方式，优化乡村产业发展用地政策",
        "引导县域金融机构支持乡村产业",
        "增加绿色优质农产品供给",
        "保护和开发农业文化遗产、传统建筑等",
        "推动农业与旅游、教育、康养等产业深度融合",
        "发展生态循环农业，健全生态保护补偿机制",
        "巩固农村基本经营制度，健全乡村振兴投入保障机制",
        "优化乡村规划建设"
    ]

    # 使用 asyncio.gather 并发执行所有异步任务
    tasks = []
    for natural_condition in natural_factors:
        tasks.append(analysis_agent.generate_analysis("natural", natural_condition))
    for policy_condition in policy_factors:
        tasks.append(analysis_agent.generate_analysis("policy", policy_condition))

    # 收集所有结果
    results = await asyncio.gather(*tasks)

    # 格式化输出自然条件分析报告
    for result in results:
        if "Local_Conditions" in result and "Natural" in result["Local_Conditions"]:
            print("\n### 自然条件分析报告")
            for condition, analysis in result["Local_Conditions"]["Natural"].items():
                print(f"\n#### {condition}")
                print(analysis)
                print("\n---")

        if "Local_Conditions" in result and "Policy" in result["Local_Conditions"]:
            print("\n### 政策分析报告")
            for condition, analysis in result["Local_Conditions"]["Policy"].items():
                print(f"\n#### {condition}")
                print(analysis)
                print("\n---")


# 运行测试
if __name__ == "__main__":
    asyncio.run(main())