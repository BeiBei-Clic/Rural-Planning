import os
from typing import Dict, Any
import asyncio
from langchain_openai import ChatOpenAI

from memory.draft import rural_DraftState


class ConditionAgent:
    """
    条件分析智能体，用于从 Markdown 文件读取内容并生成自然条件或政策分析报告。
    """

    def __init__(self, draft: rural_DraftState, analysis_type: str):
        """
        初始化条件分析智能体。

        :param draft: rural_DraftState 实例，包含村庄名称、文件路径等信息
        :param analysis_type: 分析类型，"natural" 表示自然条件分析，"policy" 表示政策分析
        """
        self.draft = draft
        self.analysis_type = analysis_type  # 分析类型

    async def generate_analysis(self) -> Dict[str, Any]:
        """
        生成分析报告。

        :return: 更新后的 draft_state，包含生成的分析报告
        """
        # 根据分析类型构造提示信息
        if self.analysis_type == "natural":
            prompt = self._construct_natural_analysis_prompt()
        elif self.analysis_type == "policy":
            prompt = self._construct_policy_analysis_prompt()
        else:
            raise ValueError("Invalid analysis type. Use 'natural' or 'policy'.")

        # 调用模型生成分析报告
        response = await ChatOpenAI(model_name=self.draft["model"]).ainvoke([{"role": "user", "content": prompt}])

        # 更新 draft_state，添加新的报告版本
        if self.analysis_type == "natural":
            self.draft["Location_Conditions"]["Natural_Conditions"] = response.content
        elif self.analysis_type == "policy":
            self.draft["Location_Conditions"]["Policy"] = response.content

        return self.draft

    def _construct_natural_analysis_prompt(self) -> str:
        """
        构造自然条件分析的提示信息。
        """
        return f'''
请根据以下 Markdown 文件内容生成{self.draft["Village_name"]}村的自然条件区位分析报告：

{self.draft["Document"]}

请按照以下五个方向进行分析，每个方向必须提供具体的案例依据，不能凭空想象：

1. **地形与地貌**
   - 总结村庄的地形和地貌特征。
   - 提供具体的案例，说明地形如何影响村庄的农业、交通或居住条件。

2. **气候条件**
   - 总结村庄的气候特征（如降水、温度、季节变化等）。
   - 提供具体的案例，说明气候条件如何影响村庄的农业生产或生活。

3. **水资源与灌溉**
   - 总结村庄的水资源状况（如河流、湖泊、地下水等）。
   - 提供具体的案例，说明水资源如何影响村庄的灌溉和生活用水。

4. **土壤质量**
   - 总结村庄的土壤质量（如肥力、酸碱度、类型等）。
   - 提供具体的案例，说明土壤质量如何影响村庄的农作物种植。

5. **自然灾害风险**
   - 总结村庄可能面临的自然灾害（如洪水、干旱、地震等）。
   - 提供具体的案例，说明村庄如何应对这些自然灾害。

**要求**：
- 每个方向必须提供具体的案例依据，不能凭空想象。
- 如果某个方向没有明确的自然条件或案例依据，请说明原因，并建议进一步研究的方向。
- 结合文档分析，但不用完全依赖文档内容，结合你对自然条件的理解和案例分析。
- 先看看{self.draft["Village_name"]}村的自然条件优势，搜寻类似有用类似区位条件的村庄的成功和失败案例，分析该自然条件是区位优势还是劣势。
- 得出优势劣势这个结论后，解释这个结论是通过分析哪个村庄的案例得出的，具体描述这个案例。
- 最后的回答要包括具体的自然条件，出自哪份文件，给出具体的文件内容；分析该自然条件的区位优势劣势；该结论是参考了什么村庄的案例，详细分析该村庄的案例。
- 如果某个方向没有明确的自然条件或案例依据，请说明原因，并建议进一步研究的方向。
'''

    def _construct_policy_analysis_prompt(self) -> str:
        """
        构造政策分析的提示信息。
        """
        return f'''
请根据以下 Markdown 文件内容生成{self.draft["Village_name"]}村的政策分析报告：

{self.draft["Document"]}

请按照以下五个方向进行分析，每个方向必须提供具体的案例依据，不能凭空想象：

1. **财政补贴与产业扶持**
   - 总结政策中关于财政补贴和产业扶持的内容。
   - 提供具体的案例，说明政策如何通过财政补贴或扶持措施支持相关产业发展。

2. **土地权益保障**
   - 总结政策中关于土地权益保障的内容。
   - 提供具体的案例，说明政策如何保障农民或企业的土地权益。

3. **农业保险与风险兜底**
   - 总结政策中关于农业保险和风险兜底的内容。
   - 提供具体的案例，说明政策如何通过保险或风险兜底机制降低农业风险。

4. **科技赋能与数字农业**
   - 总结政策中关于科技赋能和数字农业的内容。
   - 提供具体的案例，说明政策如何通过科技手段或数字农业技术提升农业生产效率。

5. **产业融合与创业支持**
   - 总结政策中关于产业融合和创业支持的内容。
   - 提供具体的案例，说明政策如何通过产业融合或创业支持措施促进经济发展。

**要求**：
- 每个方向必须提供具体的案例依据，不能凭空想象。
- 如果某个方向没有明确的政策支持或案例依据，请说明原因，并建议进一步研究的方向。
- 结合文档分析，但不用完全依赖文档内容，结合你对政策的理解和案例分析。
- 先看看{self.draft["Village_name"]}村享受的政策优势，搜寻类似政策在其他村的成功和失败的案例，分析该政策为区位优势还是劣势。
- {self.draft["Village_name"]}有什么政策区位，该区位是优势还是劣势，这个结论是通过分析哪个村庄的案例得出的，具体描述这个案例。
- 最后的回答要包括哪个具体的政策，出自哪份文件，给出具体的政策文件，给出具体的政策文件措施；分析该政策的区位优势劣势；该结论是参考了什么村庄的案例，详细分析该村庄的案例。
- 如果某个方向没有明确的政策支持或案例依据，请说明原因，并建议进一步研究的方向。
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
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
                markdown_files[os.path.splitext(filename)[0]] = content

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
        Location_Conditions={}
    )

    # 初始化条件分析智能体，选择分析类型（"natural" 或 "policy"）
    analysis_agent = ConditionAgent(draft=draft, analysis_type="natural")  # 或 "policy"

    # 生成分析报告
    updated_draft_state = await analysis_agent.generate_analysis()

    # 打印生成的分析报告
    if "Natural_Conditions" in updated_draft_state["Location_Conditions"]:
        print("自然条件分析报告:")
        print(updated_draft_state["Location_Conditions"]["Natural_Conditions"])
    elif "Policy" in updated_draft_state["Location_Conditions"]:
        print("政策分析报告:")
        print(updated_draft_state["Location_Conditions"]["Policy"])


# 运行测试
if __name__ == "__main__":
    asyncio.run(main())