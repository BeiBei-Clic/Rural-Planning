import asyncio
from typing import Dict, Any, List, Tuple
from langchain_openai import ChatOpenAI
import re
import os

from memory.draft import rural_DraftState
from save_to_local import save_dict_to_file

from dotenv import load_dotenv
load_dotenv()


class Executor:
    """
    乡村发展规划智能体，用于并行规划乡村发展的多个方面。
    """

    def __init__(self):
        """
        初始化乡村发展规划智能体。
        """
        self.planning_tasks = {
            "current_core_industry": "核心产业现状与上下游布局规划",
            "future_core_industry": "未来核心产业发展与上下游布局规划",
            "primary_industry": "第一产业发展方案",
            "secondary_industry": "第二产业发展方案",
            "tertiary_industry": "第三产业发展方案",
            "infrastructure": "基础设施建设发展方案",
            "ecological_protection": "生态环境保护发展方案",
            "brand_building": "品牌建设发展方案",
            "marketing": "市场推广和营销发展方案",
            "monitoring": "检测和评估体系发展方案",
            "policy_support": "政策支持和资金保障发展方案"
        }

    async def plan_current_core_industry(self, draft: rural_DraftState) -> Dict[str, Any]:
        """
        规划当前核心产业的发展现状与上下游布局。

        :param draft: rural_DraftState 实例
        :return: 规划结果（JSON 格式）
        """
        print("开始规划当前核心产业的发展现状与上下游布局\n")
        prompt = f'''
请根据以下信息规划{draft["village_name"]}村当前核心产业{1}的发展现状与上下游布局：

**村庄基本信息**：{draft["document"]}和基本信息分析{2}

**要求**：
- 分析当前核心产业的现状和问题。
- 提出上下游布局的优化建议。
返回内容包括现状描述,问题，优化建议
'''
        try:
            response = await ChatOpenAI(model_name=draft["model"]).ainvoke([{"role": "user", "content": prompt}])
            print("当前核心产业规划完成")
            return response.content
        except Exception as e:
            print(f"规划当前核心产业时出错：{e}")
            return {"task": "current_core_industry", "error": str(e)}

    async def plan_future_core_industry(self, draft: rural_DraftState) -> Dict[str, Any]:
        """
        规划未来核心产业的发展方向与上下游布局。

        :param draft: rural_DraftState 实例
        :return: 规划结果（JSON 格式）
        """
        print("开始规划未来核心产业的发展方向与上下游布局\n")
        prompt = f'''
请根据以下信息规划{draft["village_name"]}村未来核心产业的发展方向与上下游布局：

**村庄基本信息**：{draft["document"]}和基本信息分析{3}

**要求**：
- 预测未来可能的核心产业。
- 提出上下游布局的建议。
返回内容包括
预测的核心产业,
上游布局建议,
中游布局建议,
下游布局建议
'''
        try:
            response = await ChatOpenAI(model_name=draft["model"]).ainvoke([{"role": "user", "content": prompt}])
            print("未来核心产业规划完成")
            return response.content
        except Exception as e:
            print(f"规划未来核心产业时出错：{e}")
            return {"task": "future_core_industry", "error": str(e)}

    async def plan_primary_industry(self, draft: rural_DraftState) -> Dict[str, Any]:
        """
        规划第一产业发展方案。

        :param draft: rural_DraftState 实例
        :return: 规划结果（JSON 格式）
        """
        print("开始规划第一产业发展方案\n")
        prompt = f'''
请根据以下信息规划{draft["village_name"]}村的第一产业发展方案：

**村庄基本信息**：{draft["document"]}和基本信息分析{4}

**要求**：
- 提出适合村庄的第一产业发展方向。
- 提出具体的实施步骤。
返回内容包括
发展方向,
实施步骤
'''
        try:
            response = await ChatOpenAI(model_name=draft["model"]).ainvoke([{"role": "user", "content": prompt}])
            print("第一产业发展方案规划完成")
            return response.content
        except Exception as e:
            print(f"规划第一产业发展方案时出错：{e}")
            return {"task": "primary_industry", "error": str(e)}

    async def plan_secondary_industry(self, draft: rural_DraftState) -> Dict[str, Any]:
        """
        规划第二产业发展方案。

        :param draft: rural_DraftState 实例
        :return: 规划结果（JSON 格式）
        """
        print("开始规划第二产业发展方案\n")
        prompt = f'''
请根据以下信息规划{draft["village_name"]}村的第二产业发展方案：

**村庄基本信息**：{draft["document"]}和基本信息分析{5}

**要求**：
- 提出适合村庄的第二产业发展方向。
- 提出具体的实施步骤。
返回内容包括
发展方向,
实施步骤
'''
        try:
            response = await ChatOpenAI(model_name=draft["model"]).ainvoke([{"role": "user", "content": prompt}])
            print("第二产业发展方案规划完成")
            return response.content
        except Exception as e:
            print(f"规划第二产业发展方案时出错：{e}")
            return {"task": "secondary_industry", "error": str(e)}

    async def plan_tertiary_industry(self, draft: rural_DraftState) -> Dict[str, Any]:
        """
        规划第三产业发展方案。

        :param draft: rural_DraftState 实例
        :return: 规划结果（JSON 格式）
        """
        print("开始规划第三产业发展方案\n")
        prompt = f'''
请根据以下信息规划{draft["village_name"]}村的第三产业发展方案：

**村庄基本信息**：{draft["document"]}和基本信息分析{6}

**要求**：
- 提出适合村庄的第三产业发展方向。
- 提出具体的实施步骤。
返回内容包括
发展方向,
实施步骤
'''
        try:
            response = await ChatOpenAI(model_name=draft["model"]).ainvoke([{"role": "user", "content": prompt}])
            print("第三产业发展方案规划完成")
            return response.content
        except Exception as e:
            print(f"规划第三产业发展方案时出错：{e}")
            return {"task": "tertiary_industry", "error": str(e)}

    async def plan_infrastructure(self, draft: rural_DraftState) -> Dict[str, Any]:
        """
        规划基础设施建设发展方案。

        :param draft: rural_DraftState 实例
        :return: 规划结果（JSON 格式）
        """
        print("开始规划基础设施建设发展方案\n")
        prompt = f'''
请根据以下信息规划{draft["village_name"]}村的基础设施建设发展方案：

**村庄基本信息**：{draft["document"]}和基本信息分析{7}

**要求**：
- 提出需要优先建设的基础设施。
- 提出具体的实施步骤。
返回内容包括
优先建设的基础设施,
实施步骤
'''
        try:
            response = await ChatOpenAI(model_name=draft["model"]).ainvoke([{"role": "user", "content": prompt}])
            print("基础设施建设发展方案规划完成")
            return response.content
        except Exception as e:
            print(f"规划基础设施建设发展方案时出错：{e}")
            return {"task": "infrastructure", "error": str(e)}

    async def plan_ecological_protection(self, draft: rural_DraftState) -> Dict[str, Any]:
        """
        规划生态环境保护发展方案。

        :param draft: rural_DraftState 实例
        :return: 规划结果（JSON 格式）
        """
        print("开始规划生态环境保护发展方案\n")
        prompt = f'''
请根据以下信息规划{draft["village_name"]}村的生态环境保护发展方案：

**村庄基本信息**：{draft["document"]}和基本信息分析{8}

**要求**：
- 提出生态环境保护的重点领域。
- 提出具体的实施步骤。
返回内容包括
重点领域,
实施步骤
'''
        try:
            response = await ChatOpenAI(model_name=draft["model"]).ainvoke([{"role": "user", "content": prompt}])
            print("生态环境保护发展方案规划完成")
            return response.content
        except Exception as e:
            print(f"规划生态环境保护发展方案时出错：{e}")
            return {"task": "ecological_protection", "error": str(e)}

    async def plan_brand_building(self, draft: rural_DraftState) -> Dict[str, Any]:
        """
        规划品牌建设发展方案。

        :param draft: rural_DraftState 实例
        :return: 规划结果（JSON 格式）
        """
        print("开始规划品牌建设发展方案\n")
        prompt = f'''
请根据以下信息规划{draft["village_name"]}村的品牌建设发展方案：

**村庄基本信息**：{draft["document"]}和基本信息分析{9}

**要求**：
- 提出适合村庄的品牌建设方向。
- 提出具体的实施步骤。
返回内容包括
品牌方向,
实施步骤
'''
        try:
            response = await ChatOpenAI(model_name=draft["model"]).ainvoke([{"role": "user", "content": prompt}])
            print("品牌建设发展方案规划完成")
            return response.content
        except Exception as e:
            print(f"规划品牌建设发展方案时出错：{e}")
            return {"task": "brand_building", "error": str(e)}

    async def plan_marketing(self, draft: rural_DraftState) -> Dict[str, Any]:
        """
        规划市场推广和营销发展方案。

        :param draft: rural_DraftState 实例
        :return: 规划结果（JSON 格式）
        """
        print("开始规划市场推广和营销发展方案\n")
        prompt = f'''
请根据以下信息规划{draft["village_name"]}村的市场推广和营销发展方案：

**村庄基本信息**：{draft["document"]}和基本信息分析{10}

**要求**：
- 提出适合村庄的市场推广策略。
- 提出具体的实施步骤。
返回内容包括
市场推广策略,
实施步骤
'''
        try:
            response = await ChatOpenAI(model_name=draft["model"]).ainvoke([{"role": "user", "content": prompt}])
            print("市场推广和营销发展方案规划完成")
            return response.content
        except Exception as e:
            print(f"规划市场推广和营销发展方案时出错：{e}")
            return {"task": "marketing", "error": str(e)}

    async def plan_monitoring(self, draft: rural_DraftState) -> Dict[str, Any]:
        """
        规划检测和评估体系发展方案。

        :param draft: rural_DraftState 实例
        :return: 规划结果（JSON 格式）
        """
        print("开始规划检测和评估体系发展方案\n")
        prompt = f'''
请根据以下信息规划{draft["village_name"]}村的检测和评估体系发展方案：

**村庄基本信息**：{draft["document"]}和基本信息分析{11}

**要求**：
- 提出适合村庄的检测和评估体系。
- 提出具体的实施步骤。
返回内容包括
实施步骤
'''
        try:
            response = await ChatOpenAI(model_name=draft["model"]).ainvoke([{"role": "user", "content": prompt}])
            print("检测和评估体系发展方案规划完成")
            return response.content
        except Exception as e:
            print(f"规划检测和评估体系发展方案时出错：{e}")
            return {"task": "monitoring", "error": str(e)}

    async def plan_policy_support(self, draft: rural_DraftState) -> Dict[str, Any]:
        """
        规划政策支持和资金保障发展方案。

        :param draft: rural_DraftState 实例
        :return: 规划结果（JSON 格式）
        """
        print("开始规划政策支持和资金保障发展方案\n")
        prompt = f'''
请根据以下信息规划{draft["village_name"]}村的政策支持和资金保障发展方案：

**村庄基本信息**：{draft["document"]}和基本信息分析{12}

**要求**：
- 提出适合村庄的政策支持方向。
- 提出具体的实施步骤。
返回内容包括
政策支持方向,

'''
        try:
            response = await ChatOpenAI(model_name=draft["model"]).ainvoke([{"role": "user", "content": prompt}])
            print("政策支持和资金保障发展方案规划完成")
            return response.content
        except Exception as e:
            print(f"规划政策支持和资金保障发展方案时出错：{e}")
            return {"task": "policy_support", "error": str(e)}

    async def parallel_plan(self, draft: rural_DraftState) -> Dict[str, Any]:
        """
        并行规划乡村发展的多个方面。

        :param draft: rural_DraftState 实例
        :return: 更新后的 draft_state，包含所有规划结果
        """
        print("开始并行规划乡村发展的多个方面\n")
        tasks = [
            self.plan_current_core_industry(draft),
            self.plan_future_core_industry(draft),
            self.plan_primary_industry(draft),
            self.plan_secondary_industry(draft),
            self.plan_tertiary_industry(draft),
            self.plan_infrastructure(draft),
            self.plan_ecological_protection(draft),
            self.plan_brand_building(draft),
            self.plan_marketing(draft),
            self.plan_monitoring(draft),
            self.plan_policy_support(draft)
        ]

        results = await asyncio.gather(*tasks)


        # 合并结果到 draft 中
        if "development_plan" not in draft:
            draft["development_plan"] = {}
        
        # 将字典的键转换为列表
        keys = list(self.planning_tasks.keys())
        k=0
        for result in results:
            try:
                if keys[k] not in draft["development_plan"]:
                    draft["development_plan"][keys[k]] = {}
                    draft["development_plan"][keys[k]] = result
                    k+=1
            except:
                print(result,"\n",type(result))

        print("并行规划完成")
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
        model="google/gemini-2.0-flash-001",
    )

    # 初始化乡村发展规划智能体
    development_agent = Executor()

    # 并行规划乡村发展
    result_draft = asyncio.run(development_agent.parallel_plan(draft=draft))

    save_dict_to_file(result_draft["development_plan"], "Results", f"{result_draft["village_name"]}乡村振兴规划报告", "markdown")