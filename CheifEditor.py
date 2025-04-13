import os
from typing import Dict, Callable, Any
from langgraph.graph import StateGraph, END
import asyncio

from memory.draft import rural_DraftState
from . import NatureAnalyseAgent,PolicyAnalyseAgent



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


# 定义工作流管理器
class CheifEditor:
    def __init__(self, draft:rural_DraftState):
        """
        初始化工作流管理器。

        :param draft: 当前的工作状态，包含报告的草稿、审核意见等信息。
        """
        self.draft = draft
        self.draft["Document"] = read_markdown_files(self.draft["Documents_path"])

    def initialize_agents(self) -> Dict[str, Callable[[rural_DraftState], rural_DraftState]]:
        return {
            "Nature_Analysis": NatureAnalyseAgent(self.draft),
            "Policy_Analysis": PolicyAnalyseAgent(self.draft),
        }
        

    def _create_workflow(self, agents: Dict[str, Callable[[rural_DraftState], rural_DraftState]]) -> StateGraph:
        """
        创建工作流。

        定义工作流的节点和边，描述报告生成、审核和修订的过程。

        :param agents: 包含所有子代理的字典。
        :return: 工作流图。
        """
        workflow = StateGraph(rural_DraftState)
        workflow.set_entry_point("analysis")  # 设置工作流的入口点

        workflow.add_node("Policy_Analysis", agents[""].generate_analysis)  # 添加分析节点
        workflow.add_node("review_draft", agents["reviewer"].review_draft)  # 添加审核节点
        workflow.add_node("revise_draft", agents["reviser"].revise_draft)  # 添加修订节点

        workflow.add_edge("analysis", "review_draft")  # 分析完成后进入审核
        workflow.add_edge("revise_draft", "review_draft")  # 修订完成后重新审核

        # 添加条件边：根据审核结果决定下一步
        workflow.add_conditional_edges(
            "review_draft",
            lambda result: "pass" if result["review"] == "通过" else "fail",
            {"pass": END, "fail": "revise_draft"}
        )

    
        return workflow

    async def run(self):
        """
        运行工作流。

        初始化子代理，创建工作流图，编译工作流并调用。
        """
        agents = self._initialize_agents()  # 初始化子代理
        workflow = self._create_workflow(agents)  # 创建工作流
        app = workflow.compile()  # 编译工作流
        result = await app.ainvoke(self.draft_state)  # 调用工作流


# 测试工作流
async def main():
    """
    测试工作流。

    创建初始的工作状态，初始化工作流管理器并运行。
    """
    rural_draft_state = rural_DraftState(
        draft=[],  # 初始为空列表
        village_name="海南省沙美村",
        guidelines=[
            "报告语言是否优美流畅，符合学术规范",
            "报告是否使用英语进行撰写"
            # "报告是否包含必要的图表和数据支持",
        ],
        review="",  # 初始审核意见为空
        revision_notes=[],  # 初始修订说明为空
        query="海南省沙美村的乡村发展现状分析",
        model="deepseek-chat",
    )

    workflow_manager = CheifEditor(rural_draft_state)  # 初始化工作流管理器
    await workflow_manager.run()  # 运行工作流

# 运行测试
if __name__ == "__main__":
    asyncio.run(main())

    