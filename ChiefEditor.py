import os
from typing import Dict, Callable, Any
from langgraph.graph import StateGraph, END
import asyncio

from guidelines import guidelines
from memory.draft import rural_DraftState
from ConditionExplorer import ConditionExplorer
from Navigator import Navigator
from save_to_local import save_data_to_file


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


class ChiefEditor:
    """
    工作流管理器类，用于管理乡村振兴规划报告的生成流程。
    """

    def __init__(self, draft: rural_DraftState):
        """
        初始化工作流管理器。

        :param draft: 当前的工作状态，包含报告的草稿、审核意见等信息。
        """
        self.draft = draft
        self.draft["document"] = read_markdown_files(self.draft["documents_path"])

    def initialize_agents(self) -> Dict[str, Callable[[rural_DraftState], rural_DraftState]]:
        """
        初始化子代理。

        :return: 一个字典，包含初始化的子代理。
        """
        return {
            "condition_explorer": ConditionExplorer(),
            "navigator": Navigator(),
        }

    def _create_workflow(self, agents: Dict[str, Callable[[rural_DraftState], rural_DraftState]]) -> StateGraph:
        """
        创建工作流图。

        :param agents: 初始化的子代理。
        :return: 工作流图。
        """
        workflow = StateGraph(rural_DraftState)
        workflow.add_node("condition", agents["condition_explorer"].no_operation)
        workflow.add_node("navigator", agents["navigator"].start_planning)

        workflow.set_entry_point("condition")
        workflow.add_edge("condition", "navigator")
        workflow.set_finish_point("navigator")

        return workflow

    async def run(self):
        """
        运行工作流。

        初始化子代理，创建工作流图，编译工作流并调用。
        """
        agents = self.initialize_agents()  # 初始化子代理
        workflow = self._create_workflow(agents)  # 创建工作流
        app = workflow.compile()  # 编译工作流

        result = await app.ainvoke(self.draft)  # 调用工作流
        save_data_to_file(result, "results/金田村乡村振兴规划报告.docx")  # 保存数据到文件
        return result


async def main():
    """
    测试工作流。

    创建初始的工作状态，初始化工作流管理器并运行。
    """
    draft = rural_DraftState(
        draft=[],
        village_name="金田村",
        documents_path="resource",
        model="google/gemini-2.5-pro-exp-03-25:free",
        local_condition={"natural": {}, "policy": {}},
        navigate={}
    )

    workflow_manager = ChiefEditor(draft)  # 初始化工作流管理器
    await workflow_manager.run()  # 运行工作流


if __name__ == "__main__":
    asyncio.run(main())