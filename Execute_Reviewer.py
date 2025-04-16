import asyncio
from typing import Dict, Any, List, Tuple
from langchain_openai import ChatOpenAI
import re
import os

from memory.draft import rural_DraftState
from save_to_local import save_dict_to_file

from dotenv import load_dotenv
load_dotenv()

class Execute_Reviewer:
    def __init__(self, concurrency_limit=10):
        self.concurrency_limit = concurrency_limit
        self.semaphore = asyncio.Semaphore(concurrency_limit)

    async def review(self, task: str, draft: rural_DraftState) -> Dict[str, Any]:
        async with self.semaphore:

            if "review" not in draft:
                draft["review"]={}
            if task not in draft["review"]:
                draft["review"][task] = ""

            if "审核通过" in draft["review"][task]:
                return draft["review"][task]

            print(f"开始审核{task}\n")

            if "development_plan" not in draft:
                draft["development_plan"] = {}
            if task not in draft["development_plan"]:
                draft["development_plan"][task] = ""

            prompt = f'''
审查{draft["village_name"]}村的{task}发展方案：{draft["development_plan"][task]}

**村庄基本信息**：{draft["document"]}。

{task}的发展方案要求：
不能与该方案的的其他方向有冲突。
每一点必须有真实数字作为支撑，附带数字来源。
若没有真实数字，该观点必须有推理过程以及来源
若都没有，则必须标明该点是编造的。
报告必须是markdown格式的。

若报告满足上述要求，则返回“报告审核通过”。
若不满足要求，详细列出每一点的修改建议,告知写稿人应该如何修改：
不能与该方案的的其他方向有冲突。
每一点必须有真实数字作为支撑，附带数字来源。
若没有真实数字，该观点必须有推理过程以及来源
若都没有，则必须标明该点是编造的。
报告必须是markdown格式的。
'''
            response = await ChatOpenAI(model_name=draft["model"],).ainvoke([{"role": "user", "content": prompt}])
            print(f"{task}审核完成\n")
            return response.content

    async def parallel_review(self, draft: rural_DraftState) -> Dict[str, Any]:
        print("开始并行审核\n")

        if "passed" not in draft:
            draft["passed"] = "审核不通过"
        
        try:
            tasks = [self.review(task, draft) for task in draft["development_plan"]]
        except:
            print(draft)

        results = await asyncio.gather(*tasks)

        # 合并结果到 draft 中
        if "review" not in draft:
            draft["review"] = {}

        keys = list(draft["development_plan"].keys())
        k = 0  # 用来作为draft["review"]的下标索引
        a = 0  # 记录审核是否通过
        for result in results:
            if keys[k] not in draft["review"]:
                draft["review"][keys[k]] = {}
            draft["review"][keys[k]] = result
            k += 1
            
            if "报告审核通过" in result:
                print(f"通过{k}")
                # pass
            else:
                a = 1  # 审核不通过a=1意味着要修改

        if a == 0:
            draft["passed"] = "审核通过"
        print(f"并行审核完成：{draft['passed']}\n")
        return draft  # 返回最终的 draft_state
    
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


if __name__ == "__main__":
    # 创建 rural_DraftState 实例
    draft = rural_DraftState(
        document=read_markdown_files("Resource"),
        village_name="金田村",
        model="glm-4-flash",
        development_plan={
            "当前核心产业": "当前核心产业发展方案内容...",
            "未来核心产业": "未来核心产业发展方案内容...",
            # 其他任务的发展方案内容...
        }
    )

    # 初始化审核智能体，设置并发限制为3
    review_agent = Execute_Reviewer()

    # 并行审核乡村发展规划
    reviewed_draft = asyncio.run(review_agent.parallel_review(draft=draft))

    # print(reviewed_draft)
    print(reviewed_draft["review"])
    print(reviewed_draft["passed"])