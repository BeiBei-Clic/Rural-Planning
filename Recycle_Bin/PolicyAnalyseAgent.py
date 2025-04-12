import os
from typing import Dict, Any
import asyncio
from langchain_openai import ChatOpenAI

from memory.draft import rural_DraftState

class PolicyAnalysisAgent:
    """
    政策分析智能体，用于从 Markdown 文件读取内容并生成政策分析报告。
    """

    def __init__(self, draft: rural_DraftState):
        """
        初始化政策分析智能体。

        :param draft: rural_DraftState 实例，包含村庄名称、政策文件路径等信息
        """
        self.draft = draft

    async def generate_analysis(self) -> Dict[str, Any]:
        """
        生成政策分析报告。

        :return: 更新后的 draft_state，包含生成的分析报告
        """
        # 构造提示信息，用于指导模型生成报告
        messages = [
            {
                "role": "user",
                "content": f'''
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
            }
        ]

        # 调用模型生成分析报告
        response = await ChatOpenAI(model_name=self.draft["model"]).ainvoke(messages)

        # 更新 draft_state，添加新的报告版本
        self.draft["Location_Conditions"]["Policy"] = response.content
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
    测试政策分析智能体的功能。
    """
    # 创建 rural_DraftState 实例，初始化 Markdown 文件路径、查询内容等信息
    draft = rural_DraftState(
        draft=[],  # 初始为空列表
        Village_name="金田村",  # 村庄名称
        Document=read_markdown_files("Resource"),  # 读取 Markdown 文件
        model="glm-4-flash",  # 模型名称
        Location_Conditions={}  # 初始化 Location_Conditions 键
    )

    # 初始化政策分析智能体
    analysis_agent = PolicyAnalysisAgent(draft=draft)

    # 生成分析报告
    updated_draft_state = await analysis_agent.generate_analysis()

    # 打印生成的分析报告
    print(updated_draft_state["Location_Conditions"]["Policy"])

# 运行测试
if __name__ == "__main__":
    asyncio.run(main())