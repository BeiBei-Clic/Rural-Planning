import os
from typing import Dict, Any
import asyncio
from langchain_openai import ChatOpenAI

from memory.draft import rural_DraftState


class NaturalAnalysisAgent:
    """
    自然条件区位分析智能体，用于从 Markdown 文件读取内容并生成自然条件区位分析报告。
    """

    def __init__(self, draft: rural_DraftState):
        """
        初始化自然条件区位分析智能体。

        :param draft: rural_DraftState 实例，包含村庄名称、自然条件文件路径等信息
        """
        self.draft = draft  # 存储 draft_state，用于后续分析和更新

    async def generate_analysis(self) -> Dict[str, Any]:
        """
        生成自然条件区位分析报告。

        :return: 更新后的 draft_state，包含生成的分析报告
        """
        # 构造提示信息，用于指导模型生成报告
        messages = [
            {
                "role": "user",
                "content": f'''
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
            }
        ]

        # 调用模型生成分析报告
        response = await ChatOpenAI(model_name=self.draft["model"]).ainvoke(messages)

        # 更新 draft_state，添加新的报告版本
        self.draft["Location_Conditions"]["Natural_Conditions"] = response.content
        return self.draft


def read_markdown_files(directory_path: str) -> Dict[str, str]:
    """
    读取指定路径下的所有 Markdown 文件，并将内容存储在字典中。

    :param directory_path: 包含 Markdown 文件的目录路径
    :return: 一个字典，键是文件名（不包括扩展名），值是文件内容
    """
    markdown_files = {}  # 用于存储文件名和内容的字典

    # 遍历指定目录下的所有文件
    for filename in os.listdir(directory_path):
        # 检查文件扩展名是否为 .md
        if filename.endswith(".md"):
            file_path = os.path.join(directory_path, filename)  # 获取文件的完整路径
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()  # 读取文件内容
                # 将文件名（不包括扩展名）作为键，内容作为值存储到字典中
                markdown_files[os.path.splitext(filename)[0]] = content

    return markdown_files


async def main():
    """
    测试自然条件区位分析智能体的功能。
    """
    # 创建 rural_DraftState 实例，初始化 Markdown 文件路径、查询内容等信息
    draft = rural_DraftState(
        draft=[],  # 初始为空列表
        Village_name="金田村",  # 村庄名称
        Document=read_markdown_files("Resource"),  # 读取 Markdown 文件
        model="glm-4-flash",  # 模型名称
        Location_Conditions={}  # 初始化 Location_Conditions 键
    )

    # 初始化自然条件区位分析智能体
    analysis_agent = NaturalConditionAnalysisAgent(draft=draft)

    # 生成分析报告
    updated_draft_state = await analysis_agent.generate_analysis()

    # 打印生成的分析报告
    print(updated_draft_state["Location_Conditions"]["Natural_Conditions"])


# 运行测试
if __name__ == "__main__":
    asyncio.run(main())