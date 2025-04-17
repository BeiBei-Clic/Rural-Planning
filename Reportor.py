import asyncio
from typing import Dict, Any, List, Tuple
from langchain_openai import ChatOpenAI
import re
import os

from memory.draft import rural_DraftState
from save_to_local import save_dict_to_file
from Call_Model import call_model


from dotenv import load_dotenv
load_dotenv()

class Reportor:
    def __init__(self, concurrency_limit=10):
        self.concurrency_limit = concurrency_limit
        self.semaphore = asyncio.Semaphore(concurrency_limit)

    

    async def generate_report(self, draft: rural_DraftState) -> Dict[str, Any]:
        """
        根据已有规划报告，生成综合报告。

        :param draft: rural_DraftState 实例
        :return: 综合报告（字典格式）
        """
        async with self.semaphore:
            print(f"开始生成综合报告\n")

            # 提取核心定位
            # core_positioning = await self.extract_core_positioning(draft)

            # 构建提示词
            prompt = f'''
提取{draft["village_name"]}核心发展定位作为标题并撰写一份正式的乡村规划报告。

把{draft["plan"] if "plan" in draft else "无来源"}排版成官方文件

'''

            # 调用大模型生成综合报告
            response = await call_model(self.semaphore, prompt, draft["model"])
            comprehensive_report = response.choices[0].message.content
            # print(f"综合报告生成完成\n")
            
            # 更新 draft
            if "report" not in draft:
                draft["report"] = {}
            if "position" not in draft:
                draft["position"] = {}
            draft["report"] = comprehensive_report
            # draft["position"] = core_positioning
            # print(draft["comprehensive_report"])
            return draft


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
    os.system('cls')
    # 创建 rural_DraftState 实例
    draft = rural_DraftState(
        document=read_markdown_files("Resource"),
        village_name="金田村",
        model="grok-3-mini-beta",
    plan={
            "当前核心产业": "当前核心产业发展方案内容...",
            "未来核心产业": "未来核心产业发展方案内容...",
            # 其他任务的发展方案内容...
        }
    )

    # 初始化综合报告生成智能体，设置并发限制为3
    report_generator = Reportor()

    # 生成综合报告
    result_draft = asyncio.run(report_generator.generate_report(draft=draft))

    save_dict_to_file(result_draft, "Results\Output", f"{result_draft["village_name"]}乡村振兴规划报告", "markdown",keys=["report"])