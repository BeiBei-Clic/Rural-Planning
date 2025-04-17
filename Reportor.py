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

    async def extract_core_positioning(self, draft: rural_DraftState) -> str:
        """
        从已有规划报告中提取乡村的核心定位。

        :param draft: rural_DraftState 实例
        :return: 核心定位描述
        """
        async with self.semaphore:
            print(f"开始提取核心定位\n")

            # 构建提示词
            prompt = f'''
    请根据以下规划报告内容，提炼出{draft["village_name"]}村的核心定位：
    {draft["development_plan"]}

乡村发展定位是指基于乡村的资源禀赋、地理位置、产业特色、文化传统、生态环境等综合因素，明确乡村在区域经济社会发展中的角色和功能，确定其未来发展的核心方向和目标。发展定位通常涵盖以下几个方面：

核心产业方向：明确乡村的主导产业，如农业、旅游业、生态保护等。
功能角色：确定乡村在区域发展中的功能定位，如农业生产基地、生态保护区、文化旅游目的地等。
发展目标：设定乡村未来发展的具体目标，如经济增长、生态改善、文化传承等。
资源利用：合理规划乡村资源的开发与利用，确保可持续发展。
社会效益：关注乡村居民的生活质量提升和社会和谐发展。
通过科学的乡村发展定位，可以为乡村制定清晰的发展路径，指导资源配置和政策支持，推动乡村振兴和可持续发展。
    '''

            # 调用大模型提取核心定位
            response = await call_model(self.semaphore, prompt, draft["model"])
            core_positioning = response.choices[0].message.content.strip()
            # print(f"核心定位提取完成：{core_positioning}\n")
            return core_positioning

    async def generate_report(self, draft: rural_DraftState) -> Dict[str, Any]:
        """
        根据已有规划报告，生成综合报告。

        :param draft: rural_DraftState 实例
        :return: 综合报告（字典格式）
        """
        async with self.semaphore:
            print(f"开始生成综合报告\n")

            # 提取核心定位
            core_positioning = await self.extract_core_positioning(draft)

            # 构建提示词
            prompt = f'''
    请把下面关于{draft["village_name"]}的乡村振兴规划：
    {draft["development_plan"]}
排版美化成一份完整的乡村振兴规划报告
    
    【核心定位】：
    {core_positioning}

    【输出要求】：
    把核心发展定位提炼出来作为标题
全面综合地撰写报告
    2. 报告应符合官方公文格式，使用正式语言。
    3. 每一部分内容都应该详细，逻辑清晰，有理有据，标注数据来源
    4. 输出格式为 Markdown。
    '''

            # 调用大模型生成综合报告
            response = await call_model(self.semaphore, prompt, draft["model"])
            comprehensive_report = response.choices[0].message.content
            # print(f"综合报告生成完成\n")
            
            # 更新 draft
            if "comprehensive_report" not in draft:
                draft["comprehensive_report"] = {}
            if "core_positioning" not in draft:
                draft["core_positioning"] = {}
            draft["comprehensive_report"] = comprehensive_report
            draft["core_positioning"] = core_positioning
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
        development_plan={
            "当前核心产业": "当前核心产业发展方案内容...",
            "未来核心产业": "未来核心产业发展方案内容...",
            # 其他任务的发展方案内容...
        }
    )

    # 初始化综合报告生成智能体，设置并发限制为3
    report_generator = Reportor()

    # 生成综合报告
    comprehensive_draft = asyncio.run(report_generator.generate_report(draft=draft))

    save_dict_to_file(comprehensive_draft, "Results", f"{comprehensive_draft["village_name"]}乡村振兴规划报告", "markdown",keys=["comprehensive_report"])