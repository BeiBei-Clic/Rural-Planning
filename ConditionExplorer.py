import os
from typing import Dict, Any, List
import asyncio
from langchain_openai import ChatOpenAI

from memory.draft import rural_DraftState
from guidelines import guidelines


class ConditionExplorer:
    """
    条件分析智能体，用于从 Markdown 文件读取内容并生成自然条件或政策分析报告。
    """

    def __init__(self, draft: rural_DraftState):
        """
        初始化条件分析智能体。

        :param draft: rural_DraftState 实例，包含村庄名称、文件路径等信息
        """
        self.draft = draft  # 存储 draft 实例，用于后续分析

    async def condition_explore(self, condition_type: str, condition: str) -> Dict[str, Any]:
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

        return self.draft  # 返回更新后的 draft_state

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

    async def parallel_explore(self, conditions: Dict[str, List[str]]) -> Dict[str, Any]:
        """
        并行执行条件分析。

        :param conditions: 包含自然条件和政策条件的字典
        :return: 更新后的 draft_state，包含生成的分析报告
        """
        tasks = []
        # 为每个条件创建任务
        for condition_type, condition_list in conditions.items():
            for condition in condition_list:
                tasks.append(self.condition_explore(condition_type, condition))

        # 分批执行任务以避免资源耗尽
        batch_size = 10  # 每批处理 10 个任务
        results = []
        for i in range(0, len(tasks), batch_size):
            batch_tasks = tasks[i:i + batch_size]
            batch_results = await asyncio.gather(*batch_tasks)
            results.extend(batch_results)

        # 合并结果到 draft 中
        for result in results:
            if result["Local_Conditions"].get("Natural"):
                self.draft["Local_Conditions"]["Natural"].update(result["Local_Conditions"]["Natural"])
            if result["Local_Conditions"].get("Policy"):
                self.draft["Local_Conditions"]["Policy"].update(result["Local_Conditions"]["Policy"])

        return self.draft  # 返回最终的 draft_state


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


def type_print(result_draft: Dict[str, Any]):
    """
    格式化输出分析报告。

    :param result_draft: 包含分析报告的字典
    """
    def print_nested_dict(d: Dict[str, Any], indent: int = 0):
        """
        递归打印嵌套字典的内容。

        :param d: 要打印的字典
        :param indent: 当前缩进级别
        """
        for key, value in d.items():
            if isinstance(value, dict):
                print(" " * indent + f"### {key}")
                print_nested_dict(value, indent + 4)
            else:
                print(" " * indent + f"#### {key}")
                print(" " * indent + value)
                print(" " * indent + "---")

    # 格式化输出自然条件分析报告
    if "Natural" in result_draft["Local_Conditions"]:
        print("\n### 自然条件分析报告")
        print_nested_dict(result_draft["Local_Conditions"]["Natural"])

    # 格式化输出政策分析报告
    if "Policy" in result_draft["Local_Conditions"]:
        print("\n### 政策分析报告")
        print_nested_dict(result_draft["Local_Conditions"]["Policy"])


if __name__ == "__main__":
    # 创建 rural_DraftState 实例
    draft = rural_DraftState(
        draft=[],
        Village_name="金田村",
        Document=read_markdown_files("Resource"),
        model="glm-4-flash",
        Local_Conditions={"Natural": {}, "Policy": {}},
    )

    # 初始化条件分析智能体
    analysis_agent = ConditionExplorer(draft=draft)

    # 并行执行条件分析
    result_draft = asyncio.run(analysis_agent.parallel_explore(guidelines["condition"]))

    # 输出结果
    type_print(result_draft)