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


class Executor:
    """
    乡村发展规划智能体，用于并行规划乡村发展的多个方面。
    """

    def __init__(self,concurrency_limit=10):
        """
        初始化乡村发展规划智能体。
        """
        self.planning_tasks = {
            "当前核心产业": "当前核心产业与上下游布局规划",
            "未来核心产业": "未来核心产业发展与上下游布局规划",
            "第一产业": "第一产业发展方案",
            "第二产业": "第二产业发展方案",
            "第三产业": "第三产业发展方案",
            "基础设施": "基础设施建设发展方案",
            "生态环境": "生态环境保护发展方案",
            "品牌建设": "品牌建设发展方案",
            "市场营销": "市场推广和营销发展方案",
            "检测与评价": "检测和评估体系发展方案",
            "政策与资金": "政策支持和资金保障发展方案"
        }

        self.concurrency_limit = concurrency_limit
        self.semaphore = asyncio.Semaphore(concurrency_limit)

    async def plan_current_core_industry(self, draft: rural_DraftState) -> Dict[str, Any]:
        """
        规划当前核心产业的发展现状与上下游布局。

        :param draft: rural_DraftState 实例
        :return: 规划结果（JSON 格式）
        """
        async with self.semaphore:
            if "review" not in draft:
                draft["review"] = {}
            if "当前核心产业" not in draft["review"]:
                draft["review"]["当前核心产业"] = ""         
            if "审核通过" in draft["review"]["当前核心产业"]:
                return draft["development_plan"]["当前核心产业"]
            print("开始规划当前核心产业的发展现状与上下游布局\n")
            prompt = f'''
你是一位乡村产业规划专家，任务是为{draft["village_name"]}村制定核心产业规划方案。请按照以下步骤完成分析：

【任务目标】
1. 分析当前核心产业的现状（包括规模、技术水平、市场表现）
2. 识别产业发展的关键问题至少（3个）
3. 提出上下游布局优化建议（至少2个方向）
4. 给出具体实施路径（分阶段实施计划）

【分析框架】
- 状分析：基于村庄资源禀赋、劳动力结构、交通条件等基础数据
- 问题诊断：从产业链完整性、技术瓶颈、市场竞争等维度
- 优化建议：需符合村庄实际，具有可操作性
- 实施计划：明确时间表、责任主体和预期效果

【上下文信息】
村庄基本信息：{draft["document"]}
历史规划：{draft["development_plan"]["当前核心产业"] if "development_plan" in draft else "无历史规划"}
审核意见：{draft["review"]["当前核心产业"] if "review" in draft and "当前核心产业" in draft["review"] else "无审核意见"}

【输出规范】
- 使用分点结构，避免长段落
- 问题与建议需一一对应
- 所有建议需包含实施成本估算
- 结论部分需明确优先级排序

【约束条件】
- 不得提出需要外部大规模投资的方案
- 需考虑村庄现有劳动力结构的适配性
- 建议需与村庄生态环境承载力相匹配
输出的时候不要把报告审查结果加进去

请按照上述要求完成规划，并确保建议具有可落地性。'''
            try:
                response = await call_model(self.semaphore, prompt, draft["model"])
                print("当前核心产业规划完成\n")
                return response.choices[0].message.content
            except Exception as e:
                print(f"规划当前核心产业时出错：{e}")
                return {"task": "current_core_industry", "error": str(e)}

    async def plan_future_core_industry(self, draft: rural_DraftState) -> Dict[str, Any]:
        """
        规划未来核心产业的发展方向与上下游布局。
        
        :param draft: rural_DraftState 实例
        :return: 规划结果（JSON 格式）
        """
        async with self.semaphore:
            # 初始化审核状态
            if "review" not in draft:
                draft["review"] = {}
            if "未来核心产业" not in draft["review"]:
                draft["review"]["未来核心产业"] = ""
            # 检查是否已审核通过
            if "审核通过" in draft["review"]["未来核心产业"]:
                return draft["development_plan"]["未来核心产业"]
            
            print("开始规划未来核心产业的发展方向与上下游布局\n")
            
            # 构建提示词
            prompt = f'''
    你是一位乡村产业规划专家，任务是为{draft["village_name"]}村规划未来核心产业的发展方向与上下游布局。请按照以下要求完成规划：

    【任务目标】
    1. 预测未来5-10年可能形成的核心产业（至少3个方向）
    2. 分析每个产业的上下游布局建议
    3. 提供具体实施路径和优先级排序
    4. 评估每个建议的可行性与风险

    【分析框架】
    1. **产业预测**：
    - 基于村庄资源禀赋、区位优势和政策导向
    - 结合技术发展趋势和市场需求变化
    - 提供预测依据和置信度评估

    2. **布局建议**：
    - 上游：原材料供应、技术支持、基础设施
    - 中游：生产流程优化、技术升级路径
    - 下游：市场拓展、品牌建设、销售渠道

    3. **实施规划**：
    - 短期（1-2年）：快速见效的基础建设
    - 中期（3-5年）：技术引入与人才培养
    - 长期（5-10年）：产业链延伸与品牌塑造

    【约束条件】
    - 成本可控：单个建议实施成本不超过村庄年收入的30%
    - 生态友好：所有建议需符合村庄生态环境承载力
    - 劳动力适配：建议需与村庄现有劳动力结构相匹配
    - 技术可及：建议需基于村庄可获取的技术资源

    【输出规范】
    - 使用分点结构，避免长段落
    - 每个产业建议需包含：
    - 产业名称
    - 上中下游布局建议
    - 实施优先级（高/中/低）
    - 预期收益与风险评估
    - 提供总结性建议，明确推荐方向
    输出的时候不要把报告审查结果加进去

    【上下文信息】
    村庄基本信息：{draft["document"]}
    历史规划：{draft["development_plan"]["未来核心产业"] if "development_plan" in draft else "无历史规划"}
    审核意见：{draft["review"]["未来核心产业"] if "review" in draft and "未来核心产业" in draft["review"] else "无审核意见"}

    请按照上述要求完成规划，并确保建议具有可落地性。'''
            
            try:
                # 调用模型
                response = await call_model(self.semaphore, prompt, draft["model"])
                print("未来核心产业规划完成\n")
                return response.choices[0].message.content
            except Exception as e:
                print(f"规划未来核心产业时出错：{e}")
                return {"task": "future_core_industry", "error": str(e)}

    async def plan_primary_industry(self, draft: rural_DraftState) -> Dict[str, Any]:
        """
        规划第一产业发展方案。

        :param draft: rural_DraftState 实例
        :return: 规划结果（JSON 格式）
        """
        async with self.semaphore:
            # 初始化审核状态
            if "review" not in draft:
                draft["review"] = {}
            if "第一产业" not in draft["review"]:
                draft["review"]["第一产业"] = ""

            # 检查是否已审核通过
            if "审核通过" in draft["review"]["第一产业"]:
                return draft["development_plan"]["第一产业"]

            print("开始规划第一产业发展方案\n")

            # 构建提示词
            prompt = f'''
    你是一位乡村产业规划专家，任务是为{draft["village_name"]}村规划第一产业的发展方案。请按照以下要求完成规划：

    【任务目标】
    1. 提出适合村庄的第一产业发展方向。
    2. 提出具体的实施步骤，包括短期、中期和长期目标。
    3. 评估发展方案的可行性和潜在风险。

    【分析框架】
    1. **发展方向**：
    - 基于村庄资源禀赋、气候条件和政策支持，提出适合的第一产业发展方向。
    - 提供选择该方向的依据（如资源优势、市场需求等）。
    2. **实施步骤**：
    - 短期目标（1-2年）：快速见效的措施。
    - 中期目标（3-5年）：技术引入与规模化发展。
    - 长期目标（5-10年）：产业链延伸与品牌建设。
    3. **可行性评估**：
    - 分析方案的实施成本、资源需求和技术可行性。
    - 提出潜在风险及其应对措施。

    【上下文信息】
    - 村庄基本信息：{draft["document"]}
    - 上一版发展规划：{draft["development_plan"]["第一产业"] if "development_plan" in draft else "无历史规划"}
    - 审核意见：{draft["review"]["第一产业"] if "review" in draft and "第一产业" in draft["review"] else "无审核意见"}

    【输出规范】
    - 使用分点结构，避免长段落。
    - 每个建议需包含具体实施步骤和预期效果。
    - 结论部分需明确优先级排序。
    输出的时候不要把报告审查结果加进去

    请按照上述要求完成规划，并确保建议具有可落地性。
    '''

            try:
                # 调用大模型生成规划
                response = await call_model(self.semaphore, prompt, draft["model"])
                print("第一产业发展方案规划完成\n")
                return response.choices[0].message.content
            except Exception as e:
                print(f"规划第一产业发展方案时出错：{e}")
                return {"task": "primary_industry", "error": str(e)}

    async def plan_secondary_industry(self, draft: rural_DraftState) -> Dict[str, Any]:
        """
        规划第二产业发展方案。

        :param draft: rural_DraftState 实例
        :return: 规划结果（JSON 格式）
        """
        async with self.semaphore:
            # 初始化审核状态
            if "review" not in draft:
                draft["review"] = {}
            if "第二产业" not in draft["review"]:
                draft["review"]["第二产业"] = ""

            # 检查是否已审核通过
            if "审核通过" in draft["review"]["第二产业"]:
                return draft["development_plan"]["第二产业"]

            print("开始规划第二产业发展方案\n")

            # 构建提示词
            prompt = f'''
    你是一位乡村产业规划专家，任务是为{draft["village_name"]}村规划第二产业的发展方案。请按照以下要求完成规划：

    【任务目标】
    1. 提出适合村庄的第二产业发展方向。
    2. 提出具体的实施步骤，包括短期、中期和长期目标。
    3. 评估发展方案的可行性和潜在风险。

    【分析框架】
    1. **发展方向**：
    - 基于村庄资源禀赋、区位优势和政策支持，提出适合的第二产业发展方向。
    - 提供选择该方向的依据（如资源优势、市场需求等）。
    2. **实施步骤**：
    - 短期目标（1-2年）：快速见效的措施。
    - 中期目标（3-5年）：技术引入与规模化发展。
    - 长期目标（5-10年）：产业链延伸与品牌建设。
    3. **可行性评估**：
    - 分析方案的实施成本、资源需求和技术可行性。
    - 提出潜在风险及其应对措施。

    【上下文信息】
    - 村庄基本信息：{draft["document"]}
    - 上一版发展规划：{draft["development_plan"]["第二产业"] if "development_plan" in draft else "无历史规划"}
    - 审核意见：{draft["review"]["第二产业"] if "review" in draft and "第二产业" in draft["review"] else "无审核意见"}

    【输出规范】
    - 使用分点结构，避免长段落。
    - 每个建议需包含具体实施步骤和预期效果。
    - 结论部分需明确优先级排序。
    输出的时候不要把报告审查结果加进去

    请按照上述要求完成规划，并确保建议具有可落地性。
    '''

            try:
                # 调用大模型生成规划
                response = await call_model(self.semaphore, prompt, draft["model"])
                print("第二产业发展方案规划完成\n")
                return response.choices[0].message.content
            except Exception as e:
                print(f"规划第二产业发展方案时出错：{e}")
                return {"task": "secondary_industry", "error": str(e)}

    async def plan_tertiary_industry(self, draft: rural_DraftState) -> Dict[str, Any]:
        """
        规划第三产业发展方案。

        :param draft: rural_DraftState 实例
        :return: 规划结果（JSON 格式）
        """
        async with self.semaphore:
            # 初始化审核状态
            if "review" not in draft:
                draft["review"] = {}
            if "第三产业" not in draft["review"]:
                draft["review"]["第三产业"] = ""

            # 检查是否已审核通过
            if "审核通过" in draft["review"]["第三产业"]:
                return draft["development_plan"]["第三产业"]

            print("开始规划第三产业发展方案\n")

            # 构建提示词
            prompt = f'''
    你是一位乡村产业规划专家，任务是为{draft["village_name"]}村规划第三产业的发展方案。请按照以下要求完成规划：

    【任务目标】
    1. 提出适合村庄的第三产业发展方向。
    2. 提出具体的实施步骤，包括短期、中期和长期目标。
    3. 评估发展方案的可行性和潜在风险。

    【分析框架】
    1. **发展方向**：
    - 基于村庄资源禀赋、区位优势和政策支持，提出适合的第三产业发展方向。
    - 提供选择该方向的依据（如资源优势、市场需求等）。
    2. **实施步骤**：
    - 短期目标（1-2年）：快速见效的措施。
    - 中期目标（3-5年）：技术引入与规模化发展。
    - 长期目标（5-10年）：产业链延伸与品牌建设。
    3. **可行性评估**：
    - 分析方案的实施成本、资源需求和技术可行性。
    - 提出潜在风险及其应对措施。

    【上下文信息】
    - 村庄基本信息：{draft["document"]}
    - 上一版发展规划：{draft["development_plan"]["第三产业"] if "development_plan" in draft else "无历史规划"}
    - 审核意见：{draft["review"]["第三产业"] if "review" in draft and "第三产业" in draft["review"] else "无审核意见"}

    【输出规范】
    - 使用分点结构，避免长段落。
    - 每个建议需包含具体实施步骤和预期效果。
    - 结论部分需明确优先级排序。
    输出的时候不要把报告审查结果加进去

    请按照上述要求完成规划，并确保建议具有可落地性。
    '''

            try:
                # 调用大模型生成规划
                response = await call_model(self.semaphore, prompt, draft["model"])
                print("第三产业发展方案规划完成\n")
                return response.choices[0].message.content
            except Exception as e:
                print(f"规划第三产业发展方案时出错：{e}")
                return {"task": "tertiary_industry", "error": str(e)}

    async def plan_infrastructure(self, draft: rural_DraftState) -> Dict[str, Any]:
        """
        规划基础设施建设发展方案。

        :param draft: rural_DraftState 实例
        :return: 规划结果（JSON 格式）
        """
        async with self.semaphore:
            # 初始化审核状态
            if "review" not in draft:
                draft["review"] = {}
            if "基础设施" not in draft["review"]:
                draft["review"]["基础设施"] = ""

            # 检查是否已审核通过
            if "审核通过" in draft["review"]["基础设施"]:
                return draft["development_plan"]["基础设施"]

            print("开始规划基础设施建设发展方案\n")

            # 构建提示词
            prompt = f'''
    你是一位乡村基础设施规划专家，任务是为{draft["village_name"]}村制定基础设施建设发展方案。请按照以下要求完成规划：

    【任务目标】
    1. 提出需要优先建设的基础设施（如交通、供水、供电、通信等）。
    2. 提出具体的实施步骤，包括短期、中期和长期目标。
    3. 评估发展方案的可行性和潜在风险。

    【分析框架】
    1. **优先建设的基础设施**：
    - 基于村庄现状和发展需求，提出需要优先建设的基础设施。
    - 提供选择这些基础设施的依据（如资源条件、政策支持、村民需求等）。
    2. **实施步骤**：
    - 短期目标（1-2年）：快速见效的基础设施建设。
    - 中期目标（3-5年）：完善基础设施网络。
    - 长期目标（5-10年）：实现基础设施现代化。
    3. **可行性评估**：
    - 分析方案的实施成本、资源需求和技术可行性。
    - 提出潜在风险及其应对措施。

    【上下文信息】
    - 村庄基本信息：{draft["document"]}
    - 上一版发展规划：{draft["development_plan"]["基础设施"] if "development_plan" in draft else "无历史规划"}
    - 审核意见：{draft["review"]["基础设施"] if "review" in draft and "基础设施" in draft["review"] else "无审核意见"}

    【输出规范】
    - 使用分点结构，避免长段落。
    - 每个建议需包含具体实施步骤和预期效果。
    - 结论部分需明确优先级排序。
    输出的时候不要把报告审查结果加进去

    请按照上述要求完成规划，并确保建议具有可落地性。
    '''

            try:
                # 调用大模型生成规划
                response = await call_model(self.semaphore, prompt, draft["model"])
                print("基础设施建设发展方案规划完成\n")
                return response.choices[0].message.content
            except Exception as e:
                print(f"规划基础设施建设发展方案时出错：{e}")
                return {"task": "infrastructure", "error": str(e)}

    async def plan_ecological_protection(self, draft: rural_DraftState) -> Dict[str, Any]:
        """
        规划生态环境保护发展方案。

        :param draft: rural_DraftState 实例
        :return: 规划结果（JSON 格式）
        """
        async with self.semaphore:
            # 初始化审核状态
            if "review" not in draft:
                draft["review"] = {}
            if "生态环境" not in draft["review"]:
                draft["review"]["生态环境"] = ""

            # 检查是否已审核通过
            if "审核通过" in draft["review"]["生态环境"]:
                return draft["development_plan"]["生态环境"]

            print("开始规划生态环境保护发展方案\n")

            # 构建提示词
            prompt = f'''
    你是一位乡村生态环境保护规划专家，任务是为{draft["village_name"]}村制定生态环境保护发展方案。请按照以下要求完成规划：

    【任务目标】
    1. 提出生态环境保护的重点领域（如水资源保护、森林恢复、土壤改良等）。
    2. 提出具体的实施步骤，包括短期、中期和长期目标。
    3. 评估发展方案的可行性和潜在风险。

    【分析框架】
    1. **重点领域**：
    - 基于村庄现状和生态环境需求，提出需要优先保护的生态领域。
    - 提供选择这些领域的依据（如环境现状、政策支持、村民需求等）。
    2. **实施步骤**：
    - 短期目标（1-2年）：快速见效的生态保护措施。
    - 中期目标（3-5年）：生态系统恢复与管理。
    - 长期目标（5-10年）：生态环境可持续发展。
    3. **可行性评估**：
    - 分析方案的实施成本、资源需求和技术可行性。
    - 提出潜在风险及其应对措施。

    【上下文信息】
    - 村庄基本信息：{draft["document"]}
    - 上一版发展规划：{draft["development_plan"]["生态环境"] if "development_plan" in draft else "无历史规划"}
    - 审核意见：{draft["review"]["生态环境"] if "review" in draft and "生态环境" in draft["review"] else "无审核意见"}

    【输出规范】
    - 使用分点结构，避免长段落。
    - 每个建议需包含具体实施步骤和预期效果。
    - 结论部分需明确优先级排序。
    输出的时候不要把报告审查结果加进去

    请按照上述要求完成规划，并确保建议具有可落地性。
    '''

            try:
                # 调用大模型生成规划
                response = await call_model(self.semaphore, prompt, draft["model"])
                print("生态环境保护发展方案规划完成\n")
                return response.choices[0].message.content
            except Exception as e:
                print(f"规划生态环境保护发展方案时出错：{e}")
                return {"task": "ecological_protection", "error": str(e)}

    async def plan_brand_building(self, draft: rural_DraftState) -> Dict[str, Any]:
        """
        规划品牌建设发展方案。

        :param draft: rural_DraftState 实例
        :return: 规划结果（JSON 格式）
        """
        async with self.semaphore:
            # 初始化审核状态
            if "review" not in draft:
                draft["review"] = {}
            if "品牌建设" not in draft["review"]:
                draft["review"]["品牌建设"] = ""

            # 检查是否已审核通过
            if "审核通过" in draft["review"]["品牌建设"]:
                return draft["development_plan"]["品牌建设"]

            print("开始规划品牌建设发展方案\n")

            # 构建提示词
            prompt = f'''
    你是一位乡村品牌建设规划专家，任务是为{draft["village_name"]}村制定品牌建设发展方案。请按照以下要求完成规划：

    【任务目标】
    1. 提出适合村庄的品牌建设方向（如特色农产品品牌、乡村旅游品牌等）。
    2. 提出具体的实施步骤，包括短期、中期和长期目标。
    3. 评估品牌建设方案的可行性和潜在风险。

    【分析框架】
    1. **品牌建设方向**：
    - 基于村庄资源禀赋、产业特色和市场需求，提出适合的品牌建设方向。
    - 提供选择该方向的依据（如资源优势、市场潜力等）。
    2. **实施步骤**：
    - 短期目标（1-2年）：品牌定位与初步推广。
    - 中期目标（3-5年）：品牌影响力提升与市场拓展。
    - 长期目标（5-10年）：品牌价值巩固与多元化发展。
    3. **可行性评估**：
    - 分析方案的实施成本、资源需求和技术可行性。
    - 提出潜在风险及其应对措施。

    【上下文信息】
    - 村庄基本信息：{draft["document"]}
    - 上一版发展规划：{draft["development_plan"]["品牌建设"] if "development_plan" in draft else "无历史规划"}
    - 审核意见：{draft["review"]["品牌建设"] if "review" in draft and "品牌建设" in draft["review"] else "无审核意见"}

    【输出规范】
    - 使用分点结构，避免长段落。
    - 每个建议需包含具体实施步骤和预期效果。
    - 结论部分需明确优先级排序。
    输出的时候不要把报告审查结果加进去

    请按照上述要求完成规划，并确保建议具有可落地性。
    '''

            try:
                # 调用大模型生成规划
                response = await call_model(self.semaphore, prompt, draft["model"])
                print("品牌建设发展方案规划完成\n")
                return response.choices[0].message.content
            except Exception as e:
                print(f"规划品牌建设发展方案时出错：{e}")
                return {"task": "brand_building", "error": str(e)}

    async def plan_marketing(self, draft: rural_DraftState) -> Dict[str, Any]:
        """
        规划市场推广和营销发展方案。

        :param draft: rural_DraftState 实例
        :return: 规划结果（JSON 格式）
        """
        async with self.semaphore:
            # 初始化审核状态
            if "review" not in draft:
                draft["review"] = {}
            if "市场营销" not in draft["review"]:
                draft["review"]["市场营销"] = ""

            # 检查是否已审核通过
            if "审核通过" in draft["review"]["市场营销"]:
                return draft["development_plan"]["市场营销"]

            print("开始规划市场推广和营销发展方案\n")

            # 构建提示词
            prompt = f'''
    你是一位乡村市场推广和营销规划专家，任务是为{draft["village_name"]}村制定市场推广和营销发展方案。请按照以下要求完成规划：

    【任务目标】
    1. 提出适合村庄的市场推广策略（如线上推广、线下活动、品牌合作等）。
    2. 提出具体的实施步骤，包括短期、中期和长期目标。
    3. 评估市场推广方案的可行性和潜在风险。

    【分析框架】
    1. **市场推广策略**：
    - 基于村庄资源禀赋、产业特色和目标市场需求，提出适合的市场推广策略。
    - 提供选择这些策略的依据（如市场潜力、资源优势等）。
    2. **实施步骤**：
    - 短期目标（1-2年）：快速见效的推广活动。
    - 中期目标（3-5年）：市场拓展与渠道优化。
    - 长期目标（5-10年）：品牌价值巩固与市场多元化。
    3. **可行性评估**：
    - 分析方案的实施成本、资源需求和技术可行性。
    - 提出潜在风险及其应对措施。

    【上下文信息】
    - 村庄基本信息：{draft["document"]}
    - 上一版发展规划：{draft["development_plan"]["市场营销"] if "development_plan" in draft else "无历史规划"}
    - 审核意见：{draft["review"]["市场营销"] if "review" in draft and "市场营销" in draft["review"] else "无审核意见"}

    【输出规范】
    - 使用分点结构，避免长段落。
    - 每个建议需包含具体实施步骤和预期效果。
    - 结论部分需明确优先级排序。
    输出的时候不要把报告审查结果加进去

    请按照上述要求完成规划，并确保建议具有可落地性。
    '''

            try:
                # 调用大模型生成规划
                response = await call_model(self.semaphore, prompt, draft["model"])
                print("市场推广和营销发展方案规划完成\n")
                return response.choices[0].message.content
            except Exception as e:
                print(f"规划市场推广和营销发展方案时出错：{e}")
                return {"task": "marketing", "error": str(e)}

    async def plan_monitoring(self, draft: rural_DraftState) -> Dict[str, Any]:
        """
        规划检测和评估体系发展方案。

        :param draft: rural_DraftState 实例
        :return: 规划结果（JSON 格式）
        """
        async with self.semaphore:
            # 初始化审核状态
            if "review" not in draft:
                draft["review"] = {}
            if "检测与评价" not in draft["review"]:
                draft["review"]["检测与评价"] = ""

            # 检查是否已审核通过
            if "审核通过" in draft["review"]["检测与评价"]:
                return draft["development_plan"]["检测与评价"]

            print("开始规划检测和评估体系发展方案\n")

            # 构建提示词
            prompt = f'''
    你是一位乡村检测和评估体系规划专家，任务是为{draft["village_name"]}村制定检测和评估体系发展方案。请按照以下要求完成规划：

    【任务目标】
    1. 提出适合村庄的检测和评估体系（如环境监测、产业绩效评估等）。
    2. 提出具体的实施步骤，包括短期、中期和长期目标。
    3. 评估检测和评估体系的可行性和潜在风险。

    【分析框架】
    1. **检测和评估体系设计**：
    - 基于村庄现状和发展需求，提出适合的检测和评估体系。
    - 提供选择这些体系的依据（如政策要求、村庄发展目标等）。
    2. **实施步骤**：
    - 短期目标（1-2年）：建立基础检测和评估机制。
    - 中期目标（3-5年）：完善检测网络和评估方法。
    - 长期目标（5-10年）：实现检测和评估体系的智能化和可持续发展。
    3. **可行性评估**：
    - 分析方案的实施成本、资源需求和技术可行性。
    - 提出潜在风险及其应对措施。

    【上下文信息】
    - 村庄基本信息：{draft["document"]}
    - 上一版发展规划：{draft["development_plan"]["检测与评价"] if "development_plan" in draft else "无历史规划"}
    - 审核意见：{draft["review"]["检测与评价"] if "review" in draft and "检测与评价" in draft["review"] else "无审核意见"}

    【输出规范】
    - 使用分点结构，避免长段落。
    - 每个建议需包含具体实施步骤和预期效果。
    - 结论部分需明确优先级排序。
    输出的时候不要把报告审查结果加进去

    请按照上述要求完成规划，并确保建议具有可落地性。
    '''

            try:
                # 调用大模型生成规划
                response = await call_model(self.semaphore, prompt, draft["model"])
                print("检测和评估体系发展方案规划完成\n")
                return response.choices[0].message.content
            except Exception as e:
                print(f"规划检测和评估体系发展方案时出错：{e}")
                return {"task": "monitoring", "error": str(e)}

    async def plan_policy_support(self, draft: rural_DraftState) -> Dict[str, Any]:
        """
        规划政策支持和资金保障发展方案。

        :param draft: rural_DraftState 实例
        :return: 规划结果（JSON 格式）
        """
        async with self.semaphore:
            # 初始化审核状态
            if "review" not in draft:
                draft["review"] = {}
            if "政策与资金" not in draft["review"]:
                draft["review"]["政策与资金"] = ""

            # 检查是否已审核通过
            if "审核通过" in draft["review"]["政策与资金"]:
                return draft["development_plan"]["政策与资金"]

            print("开始规划政策支持和资金保障发展方案\n")

            # 构建提示词
            prompt = f'''
    你是一位乡村政策支持和资金保障规划专家，任务是为{draft["village_name"]}村制定政策支持和资金保障发展方案。请按照以下要求完成规划：

    【任务目标】
    1. 提出适合村庄的政策支持方向（如农业补贴、基础设施建设支持等）。
    2. 提出具体的实施步骤，包括短期、中期和长期目标。
    3. 评估政策支持和资金保障方案的可行性和潜在风险。

    【分析框架】
    1. **政策支持方向**：
    - 基于村庄现状和发展需求，提出适合的政策支持方向。
    - 提供选择这些方向的依据（如政策导向、村庄发展目标等）。
    2. **实施步骤**：
    - 短期目标（1-2年）：快速见效的政策支持措施。
    - 中期目标（3-5年）：政策体系完善与资金保障优化。
    - 长期目标（5-10年）：政策支持的可持续发展。
    3. **可行性评估**：
    - 分析方案的实施成本、资源需求和技术可行性。
    - 提出潜在风险及其应对措施。

    【上下文信息】
    - 村庄基本信息：{draft["document"]}
    - 上一版发展规划：{draft["development_plan"]["政策与资金"] if "development_plan" in draft else "无历史规划"}
    - 审核意见：{draft["review"]["政策与资金"] if "review" in draft and "政策与资金" in draft["review"] else "无审核意见"}

    【输出规范】
    - 使用分点结构，避免长段落。
    - 每个建议需包含具体实施步骤和预期效果。
    - 结论部分需明确优先级排序。
    输出的时候不要把报告审查结果加进去

    请按照上述要求完成规划，并确保建议具有可落地性。
    '''

            try:
                # 调用大模型生成规划
                response = await call_model(self.semaphore, prompt, draft["model"])
                print("政策支持和资金保障发展方案规划完成\n")
                return response.choices[0].message.content
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

        # if "review" in draft:
        #     for review in draft["review"]:
                # print(f"{review}：\n{draft["review"][review]}\n")

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
            # self.plan_policy_support(draft)
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


        print("并行规划完成\n")
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
    os.system('cls')
    # 创建 rural_DraftState 实例
    draft = rural_DraftState(
        document=read_markdown_files("Resource"),
        village_name="金田村",
        model="grok-3-mini-beta",
    )

    # 初始化乡村发展规划智能体
    development_agent = Executor()

    # 并行规划乡村发展
    result_draft = asyncio.run(development_agent.parallel_plan(draft=draft))

    save_dict_to_file(result_draft["development_plan"], "Results", f"{result_draft["village_name"]}乡村振兴规划报告", "markdown")