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

    def __init__(self,concurrency_limit=60):
        """
        初始化乡村发展规划智能体。
        """
        self.planning_tasks = {
            "产业发展定位": "国家政策框架分析",
            "产业发展思路": "地方配套措施",
            "产业体系构建": "农产品电商渠道拓展",
            "第一产业": "新型农业经营主体培育方案",
            "第二产业": "数字化公共服务体系建立方案",
            "第三产业": "社会治理与公共服务提升方案",
            "基础设施": "资源整合与产业布局优化发展方案",
            "生态环境": "品牌建设发展方案",
            "品牌建设": "市场推广和营销发展方案",
            "市场推广":"",
            "监测评估":"",
            "政策资金支持":""
        }

        self.concurrency_limit = concurrency_limit
        self.semaphore = asyncio.Semaphore(concurrency_limit)

    async def industry_positioning(self, draft: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析区域产业发展定位的现状、问题及优化建议，提供科学合理的产业布局方案。

        :param draft: 包含产业发展相关信息的字典
        :return: 分析结果（JSON 格式）
        """
        async with self.semaphore:
            if "review" not in draft:
                draft["review"] = {}
            if "产业发展定位" not in draft["review"]:
                draft["review"]["产业发展定位"] = ""
            if "审核通过" in draft["review"]["产业发展定位"]:
                return draft["plan"]["产业发展定位"]
            
            print("开始分析区域产业发展定位\n")
            prompt = f'''
    你是一位产业经济分析师，任务是分析区域产业发展定位的现状、问题及优化建议。请按照以下步骤完成分析：

    【任务目标】
    1. 分析当前区域产业定位的现状（包括主导产业、竞争优势、产业链完整性）
    2. 识别产业发展中的关键问题（至少3个）
    3. 提出优化建议（至少2个方向）
    4. 给出具体实施路径（分阶段实施计划）

    【分析框架】
    - 现状分析：基于区域经济数据、产业分布和政策支持
    - 问题诊断：从产业链协同、技术创新、市场竞争力等维度
    - 优化建议：需符合区域资源禀赋，具有可操作性
    - 实施计划：明确时间表、责任主体和预期效果

    【上下文信息】
    历史分析：{draft["plan"]["产业发展定位"] if "plan" in draft and "产业发展定位" in draft["plan"] else "无历史分析"}
    审核意见：{draft["review"]["产业发展定位"] if "review" in draft and "产业发展定位" in draft["review"] else "无审核意见"}
    已有信息：{draft["plan"] if "plan" in draft else "暂无已有规划"}

    【输出规范】
    - 使用分点结构，避免长段落
    - 问题与建议需一一对应
    - 所有建议需包含实施成本估算
    - 结论部分需明确优先级排序

    【约束条件】
    - 优化建议需与区域资源承载能力相匹配
    - 需考虑产业协同发展和链式效应
    - 建议需与国家产业政策导向保持一致
    输出的时候不要把报告审查结果加进去

    请按照上述要求完成分析，并确保建议具有可落地性。'''
            try:
                response = await call_model(self.semaphore, prompt, draft["model"])
                print("产业发展分析完成\n")
                return response.choices[0].message.content
            except Exception as e:
                print(f"产业发展定位时出错：{e}")
                return {"task": "industry_positioning_analysis", "error": str(e)}

    async def industry_development(self, draft: rural_DraftState) -> Dict[str, Any]:
        """
        分析区域产业发展现状，提出科学合理的产业发展思路与实施路径。
        
        :param draft: rural_DraftState 实例
        :return: 产业发展规划结果（JSON 格式）
        """
        async with self.semaphore:
            # 初始化审核状态
            if "review" not in draft:
                draft["review"] = {}
            if "产业发展思路" not in draft["review"]:
                draft["review"]["产业发展思路"] = ""
            # 检查是否已审核通过
            if "审核通过" in draft["review"]["产业发展思路"]:
                return draft["plan"]["产业发展思路"]
            
            print("开始分析区域产业发展思路\n")
            
            # 构建提示词
            prompt = f'''
    你是一位产业经济规划专家，任务是为{draft["village_name"]}村制定科学合理的产业发展思路。请按照以下要求完成规划：

    【任务目标】
    1. 分析区域产业发展的现状与优势（至少3个维度）。
    2. 识别产业发展中的关键制约因素（至少3个）。
    3. 提出产业发展方向与重点（至少2个方向）。
    4. 制定具体实施路径与优先级排序。
    5. 评估方案的可行性和潜在风险。

    【分析框架】
    1. **现状分析**：
    - 产业基础：现有主导产业、规模与竞争力。
    - 资源禀赋：自然资源、人力资源与技术资源。
    - 政策环境：现有政策支持与实施效果。

    2. **问题诊断**：
    - 产业链短板：关键环节缺失或薄弱点。
    - 市场竞争力：产品差异化与品牌建设情况。
    - 技术创新：研发能力与技术应用水平。
    - 人才短缺：专业人才储备与引进难度。

    3. **发展方向建议**：
    - 产业延链：补齐产业链关键环节的具体建议。
    - 产业融合：推动一二三产业融合的创新模式。
    - 数字赋能：利用数字技术提升产业效率的路径。
    - 品牌建设：打造区域特色品牌的策略与方法。

    4. **实施规划**：
    - 短期（1-2年）：快速见效的基础建设和关键环节突破。
    - 中期（3-5年）：产业链完善、技术引入与人才培养。
    - 长期（5-10年）：产业集群形成、品牌塑造与市场拓展。

    5. **可行性评估**：
    - 分析方案的实施成本、资源需求和技术可行性。
    - 提出潜在风险及其应对措施。

    【约束条件】
    - 成本可控：总投入不超过地方财政预算的15%。
    - 政策合规：建议需与国家和地方产业政策保持一致。
    - 技术可及：建议需基于区域可获取的技术资源。
    - 生态友好：产业发展需符合区域生态保护要求。
    - 公众参与：建议需考虑村民接受度和参与度。

    【输出规范】
    - 使用分点结构，避免长段落。
    - 每项建议需包含：
    - 措施名称
    - 具体内容
    - 实施优先级（高/中/低）
    - 预期效果与风险评估
    - 成本估算与资金来源
    - 提供总结性建议，明确推荐方向
    输出的时候不要把报告审查结果加进去

    【上下文信息】
    地方基本信息：{draft["document"]}
    中央政策文件：《数字乡村发展战略纲要》、《数字乡村发展行动计划（2022-2025年）》
    历史规划：{draft["plan"]["产业发展思路"] if "plan" in draft and "产业发展思路" in draft["plan"] else "无历史规划"}
    审核意见：{draft["review"]["产业发展思路"] if "review" in draft and "产业发展思路" in draft["review"] else "无审核意见"}
        已有信息：{draft["plan"] if "plan" in draft else "暂无已有规划"}

    【参考案例】
    成功案例：《江苏省数字乡村产业发展规划》提出的"一村一品"数字化转型路径
    政策支持：相关财政补贴、税收优惠和金融创新产品案例

    请按照上述要求完成规划，并确保建议具有可落地性。'''
            
            try:
                # 调用模型
                response = await call_model(self.semaphore, prompt, draft["model"])
                print("产业发展思路规划完成\n")
                return response.choices[0].message.content
            except Exception as e:
                print(f"产业发展思路制定时出错：{e}")
                return {"task": "industry_development_plan", "error": str(e)}

    async def industry_system(self, draft: rural_DraftState) -> Dict[str, Any]:
        """
        构建区域产业体系，推动产业协同发展与数字化转型。
        
        :param draft: rural_DraftState 实例
        :return: 产业体系构建规划结果（JSON 格式）
        """
        async with self.semaphore:
            # 初始化审核状态
            if "review" not in draft:
                draft["review"] = {}
            if "产业体系构建" not in draft["review"]:
                draft["review"]["产业体系构建"] = ""
            # 检查是否已审核通过
            if "审核通过" in draft["review"]["产业体系构建"]:
                return draft["plan"]["产业体系构建"]
            
            print("开始构建区域产业体系规划\n")
            
            # 构建提示词
            prompt = f'''
    你是一位产业体系规划专家，任务是为{draft["village_name"]}村构建科学合理的区域产业体系。请按照以下要求完成规划：

    【任务目标】
    1. 分析区域产业体系的现状与优势（至少3个维度）。
    2. 识别产业体系构建中的关键问题（至少3个）。
    3. 提出产业体系优化建议（至少5项）。
    4. 提供具体实施路径与优先级排序。
    5. 评估每个建议的可行性和潜在风险。

    【分析框架】
    1. **现状分析**：
    - 产业基础：现有主导产业、产业链完整性和市场竞争力。
    - 资源禀赋：自然资源、人力资源和技术资源的利用情况。
    - 政策环境：现有政策支持与实施效果。

    2. **问题诊断**：
    - 产业链短板：关键环节缺失或薄弱点。
    - 技术创新能力：研发能力与技术应用水平。
    - 产业协同效应：一二三产业融合发展情况。
    - 品牌建设：区域特色品牌塑造与市场认知度。

    3. **优化建议**：
    - 产业链延伸：补齐产业链关键环节的具体建议。
    - 产业融合：推动一二三产业融合的创新模式。
    - 技术赋能：利用数字技术提升产业效率的路径。
    - 品牌塑造：打造区域特色品牌的策略与方法。
    - 政策配套：完善产业支持政策的具体建议。

    4. **实施规划**：
    - 短期（1-2年）：快速见效的基础建设和关键环节突破。
    - 中期（3-5年）：产业链完善、技术引入与人才培养。
    - 长期（5-10年）：产业集群形成、品牌塑造与市场拓展。

    5. **可行性评估**：
    - 分析方案的实施成本、资源需求和技术可行性。
    - 提出潜在风险及其应对措施。

    【约束条件】
    - 成本可控：总投入不超过地方财政预算的15%。
    - 政策合规：建议需与国家和地方产业政策保持一致。
    - 技术可及：建议需基于区域可获取的技术资源。
    - 生态友好：产业发展需符合区域生态保护要求。
    - 公众参与：建议需考虑村民接受度和参与度。

    【输出规范】
    - 使用分点结构，避免长段落。
    - 每项建议需包含：
    - 措施名称
    - 具体内容
    - 实施优先级（高/中/低）
    - 预期效果与风险评估
    - 成本估算与资金来源
    - 提供总结性建议，明确推荐方向
    输出的时候不要把报告审查结果加进去

    【上下文信息】
    村庄基本信息：{draft["document"]}
    中央政策文件：《数字乡村发展战略纲要》、《数字乡村发展行动计划（2022-2025年）》
    历史规划：{draft["plan"]["产业体系构建"] if "plan" in draft and "产业体系构建" in draft["plan"] else "无历史规划"}
    审核意见：{draft["review"]["产业体系构建"] if "review" in draft and "产业体系构建" in draft["review"] else "无审核意见"}
    已有信息：{draft["plan"] if "plan" in draft else "暂无已有规划"}

    【参考案例】
    成功案例：《浙江省数字乡村产业发展规划》提出的"一村一品"数字化转型路径
    政策支持：相关财政补贴、税收优惠和金融创新产品案例

    请按照上述要求完成规划，并确保建议具有可落地性。'''
            
            try:
                # 调用模型
                response = await call_model(self.semaphore, prompt, draft["model"])
                print("产业体系构建规划完成\n")
                return response.choices[0].message.content
            except Exception as e:
                print(f"产业体系构建规划时出错：{e}")
                return {"task": "industry_system_planning", "error": str(e)}

    async def primary_industry_planning(self, draft: rural_DraftState) -> Dict[str, Any]:
        """
        规划第一产业发展方案，推动农业、林业、畜牧业和渔业等领域的现代化发展。
        
        :param draft: rural_DraftState 实例
        :return: 第一产业发展规划结果（JSON 格式）
        """
        async with self.semaphore:
            # 初始化审核状态
            if "review" not in draft:
                draft["review"] = {}
            if "第一产业" not in draft["review"]:
                draft["review"]["第一产业"] = ""
            # 检查是否已审核通过
            if "审核通过" in draft["review"]["第一产业"]:
                return draft["plan"]["第一产业"]
            
            print("开始规划第一产业发展方案\n")
            
            # 构建提示词
            prompt = f'''
    你是一位第一产业发展规划专家，任务是为{draft["village_name"]}村规划农业、林业、畜牧业和渔业等领域的现代化发展方案。请按照以下要求完成规划：

    【任务目标】
    1. 分析第一产业的现状与优势（至少3个维度）。
    2. 识别产业发展中的关键问题（至少3个）。
    3. 提出产业发展方向与重点（至少3个方向）。
    4. 制定具体实施路径与优先级排序。
    5. 评估方案的可行性和潜在风险。

    【分析框架】
    1. **现状分析**：
    - 农业：种植结构、产量与市场竞争力。
    - 林业：森林资源利用与生态保护。
    - 畜牧业：养殖规模、品种与市场需求。
    - 渔业：水产养殖与捕捞现状。
    - 资源禀赋：自然资源、劳动力与技术条件。

    2. **问题诊断**：
    - 产业链短板：关键环节缺失或薄弱点。
    - 技术创新能力：研发能力与技术应用水平。
    - 市场竞争力：产品差异化与品牌建设情况。
    - 生态保护：产业发展与生态保护的平衡问题。

    3. **发展方向建议**：
    - 产业延链：补齐产业链关键环节的具体建议。
    - 数字赋能：利用数字技术提升产业效率的路径。
    - 生态友好：推动绿色发展的具体措施。
    - 品牌建设：打造区域特色品牌的策略与方法。

    4. **实施规划**：
    - 短期（1-2年）：快速见效的基础建设和关键环节突破。
    - 中期（3-5年）：技术引入、人才培养和产业链完善。
    - 长期（5-10年）：产业集群形成、品牌塑造与市场拓展。

    5. **可行性评估**：
    - 分析方案的实施成本、资源需求和技术可行性。
    - 提出潜在风险及其应对措施。

    【约束条件】
    - 成本可控：总投入不超过地方财政预算的15%。
    - 政策合规：建议需与国家和地方产业政策保持一致。
    - 技术可及：建议需基于区域可获取的技术资源。
    - 生态友好：产业发展需符合区域生态保护要求。
    - 公众参与：建议需考虑村民接受度和参与度。

    【输出规范】
    - 使用分点结构，避免长段落。
    - 每项建议需包含：
    - 措施名称
    - 具体内容
    - 实施优先级（高/中/低）
    - 预期效果与风险评估
    - 成本估算与资金来源
    - 提供总结性建议，明确推荐方向
    输出的时候不要把报告审查结果加进去

    【上下文信息】
    村庄基本信息：{draft["document"]}
    中央政策文件：《数字乡村发展战略纲要》、《数字乡村发展行动计划（2022-2025年）》
    历史规划：{draft["plan"]["第一产业"] if "plan" in draft and "第一产业" in draft["plan"] else "无历史规划"}
    审核意见：{draft["review"]["第一产业"] if "review" in draft and "第一产业" in draft["review"] else "无审核意见"}
    已有信息：{draft["plan"] if "plan" in draft else "暂无已有规划"}

    【参考案例】
    成功案例：《浙江省数字乡村产业发展规划》提出的农业数字化转型路径
    政策支持：相关财政补贴、税收优惠和金融创新产品案例

    请按照上述要求完成规划，并确保建议具有可落地性。'''
            
            try:
                # 调用模型
                response = await call_model(self.semaphore, prompt, draft["model"])
                print("第一产业发展规划完成\n")
                return response.choices[0].message.content
            except Exception as e:
                print(f"第一产业发展规划时出错：{e}")
                return {"task": "primary_industry_planning", "error": str(e)}

    async def secondary_industry_planning(self, draft: rural_DraftState) -> Dict[str, Any]:
        """
        规划第二产业发展方案，推动制造业、建筑业、采矿业等领域的现代化发展。
        
        :param draft: rural_DraftState 实例
        :return: 第二产业发展规划结果（JSON 格式）
        """
        async with self.semaphore:
            # 初始化审核状态
            if "review" not in draft:
                draft["review"] = {}
            if "第二产业" not in draft["review"]:
                draft["review"]["第二产业"] = ""
            # 检查是否已审核通过
            if "审核通过" in draft["review"]["第二产业"]:
                return draft["plan"]["第二产业"]
            
            print("开始规划第二产业发展方案\n")
            
            # 构建提示词
            prompt = f'''
    你是一位第二产业发展规划专家，任务是为{draft["village_name"]}村规划制造业、建筑业、采矿业等领域的现代化发展方案。请按照以下要求完成规划：

    【任务目标】
    1. 分析第二产业的现状与优势（至少3个维度）。
    2. 识别产业发展中的关键问题（至少3个）。
    3. 提出产业发展方向与重点（至少3个方向）。
    4. 制定具体实施路径与优先级排序。
    5. 评估方案的可行性和潜在风险。

    【分析框架】
    1. **现状分析**：
    - 制造业：现有制造业类型、规模与技术水平。
    - 建筑业：建筑产业现状与市场需求。
    - 采矿业：矿产资源利用与开发现状。
    - 资源禀赋：自然资源、劳动力与技术条件。

    2. **问题诊断**：
    - 产业链短板：关键环节缺失或薄弱点。
    - 技术创新能力：研发能力与技术应用水平。
    - 市场竞争力：产品差异化与品牌建设情况。
    - 生态保护：产业发展与生态保护的平衡问题。

    3. **发展方向建议**：
    - 产业延链：补齐产业链关键环节的具体建议。
    - 数字赋能：利用数字技术提升产业效率的路径。
    - 生态友好：推动绿色发展的具体措施。
    - 品牌建设：打造区域特色品牌的策略与方法。

    4. **实施规划**：
    - 短期（1-2年）：快速见效的基础建设和关键环节突破。
    - 中期（3-5年）：技术引入、人才培养和产业链完善。
    - 长期（5-10年）：产业集群形成、品牌塑造与市场拓展。

    5. **可行性评估**：
    - 分析方案的实施成本、资源需求和技术可行性。
    - 提出潜在风险及其应对措施。

    【约束条件】
    - 成本可控：总投入不超过地方财政预算的15%。
    - 政策合规：建议需与国家和地方产业政策保持一致。
    - 技术可及：建议需基于区域可获取的技术资源。
    - 生态友好：产业发展需符合区域生态保护要求。
    - 公众参与：建议需考虑村民接受度和参与度。

    【输出规范】
    - 使用分点结构，避免长段落。
    - 每项建议需包含：
    - 措施名称
    - 具体内容
    - 实施优先级（高/中/低）
    - 预期效果与风险评估
    - 成本估算与资金来源
    - 提供总结性建议，明确推荐方向
    输出的时候不要把报告审查结果加进去

    【上下文信息】
    村庄基本信息：{draft["document"]}
    中央政策文件：《数字乡村发展战略纲要》、《数字乡村发展行动计划（2022-2025年）》
    历史规划：{draft["plan"]["第二产业"] if "plan" in draft and "第二产业" in draft["plan"] else "无历史规划"}
    审核意见：{draft["review"]["第二产业"] if "review" in draft and "第二产业" in draft["review"] else "无审核意见"}
    已有信息：{draft["plan"] if "plan" in draft else "暂无已有规划"}

    【参考案例】
    成功案例：《江苏省数字乡村产业发展规划》提出的制造业数字化转型路径
    政策支持：相关财政补贴、税收优惠和金融创新产品案例

    请按照上述要求完成规划，并确保建议具有可落地性。'''
            
            try:
                # 调用模型
                response = await call_model(self.semaphore, prompt, draft["model"])
                print("第二产业发展规划完成\n")
                return response.choices[0].message.content
            except Exception as e:
                print(f"第二产业发展规划时出错：{e}")
                return {"task": "secondary_industry_planning", "error": str(e)}

    async def tertiary_industry_planning(self, draft: rural_DraftState) -> Dict[str, Any]:
        """
        规划第三产业发展方案，推动服务业、旅游业等领域的现代化发展。
        
        :param draft: rural_DraftState 实例
        :return: 第三产业发展规划结果（JSON 格式）
        """
        async with self.semaphore:
            # 初始化审核状态
            if "review" not in draft:
                draft["review"] = {}
            if "第三产业" not in draft["review"]:
                draft["review"]["第三产业"] = ""
            # 检查是否已审核通过
            if "审核通过" in draft["review"]["第三产业"]:
                return draft["plan"]["第三产业"]
            
            print("开始规划第三产业发展方案\n")
            
            # 构建提示词
            prompt = f'''
    你是一位第三产业发展规划专家，任务是为{draft["village_name"]}村规划服务业、旅游业等领域的现代化发展方案。请按照以下要求完成规划：

    【任务目标】
    1. 分析第三产业的现状与优势（至少3个维度）。
    2. 识别产业发展中的关键问题（至少3个）。
    3. 提出产业发展方向与重点（至少3个方向）。
    4. 制定具体实施路径与优先级排序。
    5. 评估方案的可行性和潜在风险。

    【分析框架】
    1. **现状分析**：
    - 服务业：现有服务类型、规模与市场需求。
    - 旅游业：旅游资源开发与游客接待情况。
    - 物流业：物流基础设施与配送效率。
    - 资源禀赋：自然资源、劳动力与技术条件。

    2. **问题诊断**：
    - 产业链短板：关键环节缺失或薄弱点。
    - 技术创新能力：数字化服务能力和技术应用水平。
    - 市场竞争力：服务差异化与品牌建设情况。
    - 生态保护：产业发展与生态保护的平衡问题。

    3. **发展方向建议**：
    - 产业延链：补齐产业链关键环节的具体建议。
    - 数字赋能：利用数字技术提升服务效率的路径。
    - 生态友好：推动绿色发展的具体措施。
    - 品牌建设：打造区域特色品牌的策略与方法。

    4. **实施规划**：
    - 短期（1-2年）：快速见效的基础建设和关键环节突破。
    - 中期（3-5年）：技术引入、人才培养和产业链完善。
    - 长期（5-10年）：产业集群形成、品牌塑造与市场拓展。

    5. **可行性评估**：
    - 分析方案的实施成本、资源需求和技术可行性。
    - 提出潜在风险及其应对措施。

    【约束条件】
    - 成本可控：总投入不超过地方财政预算的15%。
    - 政策合规：建议需与国家和地方产业政策保持一致。
    - 技术可及：建议需基于区域可获取的技术资源。
    - 生态友好：产业发展需符合区域生态保护要求。
    - 公众参与：建议需考虑村民接受度和参与度。

    【输出规范】
    - 使用分点结构，避免长段落。
    - 每项建议需包含：
    - 措施名称
    - 具体内容
    - 实施优先级（高/中/低）
    - 预期效果与风险评估
    - 成本估算与资金来源
    - 提供总结性建议，明确推荐方向
    输出的时候不要把报告审查结果加进去

    【上下文信息】
    村庄基本信息：{draft["document"]}
    中央政策文件：《数字乡村发展战略纲要》、《数字乡村发展行动计划（2022-2025年）》
    历史规划：{draft["plan"]["第三产业"] if "plan" in draft and "第三产业" in draft["plan"] else "无历史规划"}
    审核意见：{draft["review"]["第三产业"] if "review" in draft and "第三产业" in draft["review"] else "无审核意见"}
    已有信息：{draft["plan"] if "plan" in draft else "暂无已有规划"}

    【参考案例】
    成功案例：《云南省数字乡村产业发展规划》提出的乡村旅游数字化转型路径
    政策支持：相关财政补贴、税收优惠和金融创新产品案例

    请按照上述要求完成规划，并确保建议具有可落地性。'''
            
            try:
                # 调用模型
                response = await call_model(self.semaphore, prompt, draft["model"])
                print("第三产业发展规划完成\n")
                return response.choices[0].message.content
            except Exception as e:
                print(f"第三产业发展规划时出错：{e}")
                return {"task": "tertiary_industry_planning", "error": str(e)}

    async def infrastructure_planning(self, draft: rural_DraftState) -> Dict[str, Any]:
        """
        规划基础设施建设方案，推动交通、通信、能源、公共服务等领域的现代化发展。
        
        :param draft: rural_DraftState 实例
        :return: 基础设施建设规划结果（JSON 格式）
        """
        async with self.semaphore:
            # 初始化审核状态
            if "review" not in draft:
                draft["review"] = {}
            if "基础设施" not in draft["review"]:
                draft["review"]["基础设施"] = ""
            # 检查是否已审核通过
            if "审核通过" in draft["review"]["基础设施"]:
                return draft["plan"]["基础设施"]
            
            print("开始规划基础设施建设方案\n")
            
            # 构建提示词
            prompt = f'''
    你是一位基础设施规划专家，任务是为{draft["village_name"]}村规划交通、通信、能源、公共服务等领域的现代化发展方案。请按照以下要求完成规划：

    【任务目标】
    1. 分析基础设施的现状与优势（至少3个维度）。
    2. 识别基础设施建设中的关键问题（至少3个）。
    3. 提出基础设施建设方向与重点（至少3个方向）。
    4. 制定具体实施路径与优先级排序。
    5. 评估方案的可行性和潜在风险。

    【分析框架】
    1. **现状分析**：
    - 交通：现有交通网络、道路状况与物流能力。
    - 通信：网络覆盖、数字化基础设施现状。
    - 能源：电力供应、可再生能源利用情况。
    - 公共服务：教育、医疗、文化等设施现状。
    - 资源禀赋：自然资源、劳动力与技术条件。

    2. **问题诊断**：
    - 规划不合理：基础设施布局与产业发展需求不匹配。
    - 资金不足：建设与维护资金短缺问题。
    - 技术落后：现有基础设施的技术水平与更新需求。
    - 生态保护：基础设施建设与生态保护的平衡问题。

    3. **发展方向建议**：
    - 交通网络优化：提升物流效率和 connectivity 的具体建议。
    - 数字化基础设施：利用数字技术提升服务效率的路径。
    - 能源设施升级：推动绿色能源利用的具体措施。
    - 公共服务提升：改善教育、医疗、文化设施的策略与方法。

    4. **实施规划**：
    - 短期（1-2年）：快速见效的基础建设和关键环节突破。
    - 中期（3-5年）：技术引入、人才培养和设施完善。
    - 长期（5-10年）：全面数字化、绿色化与服务提升。

    5. **可行性评估**：
    - 分析方案的实施成本、资源需求和技术可行性。
    - 提出潜在风险及其应对措施。

    【约束条件】
    - 成本可控：总投入不超过地方财政预算的20%。
    - 政策合规：建议需与国家和地方基础设施政策保持一致。
    - 技术可及：建议需基于区域可获取的技术资源。
    - 生态友好：基础设施建设需符合区域生态保护要求。
    - 公众参与：建议需考虑村民接受度和参与度。

    【输出规范】
    - 使用分点结构，避免长段落。
    - 每项建议需包含：
    - 措施名称
    - 具体内容
    - 实施优先级（高/中/低）
    - 预期效果与风险评估
    - 成本估算与资金来源
    - 提供总结性建议，明确推荐方向
    输出的时候不要把报告审查结果加进去

    【上下文信息】
    村庄基本信息：{draft["document"]}
    中央政策文件：《数字乡村发展战略纲要》、《数字乡村发展行动计划（2022-2025年）》
    历史规划：{draft["plan"]["基础设施"] if "plan" in draft and "基础设施" in draft["plan"] else "无历史规划"}
    审核意见：{draft["review"]["基础设施"] if "review" in draft and "基础设施" in draft["review"] else "无审核意见"}
    已有信息：{draft["plan"] if "plan" in draft else "暂无已有规划"}

    【参考案例】
    成功案例：《浙江省数字乡村基础设施建设规划》提出的乡村交通和通信网络优化路径
    政策支持：相关财政补贴、税收优惠和金融创新产品案例

    请按照上述要求完成规划，并确保建议具有可落地性。'''
            
            try:
                # 调用模型
                response = await call_model(self.semaphore, prompt, draft["model"])
                print("基础设施建设规划完成\n")
                return response.choices[0].message.content
            except Exception as e:
                print(f"基础设施建设规划时出错：{e}")
                return {"task": "infrastructure_planning", "error": str(e)}

    async def ecological_protection(self, draft: rural_DraftState) -> Dict[str, Any]:
        """
        规划生态环境保护方案，推动生态修复、污染治理和资源可持续利用。
        
        :param draft: rural_DraftState 实例
        :return: 生态环境保护规划结果（JSON 格式）
        """
        async with self.semaphore:
            # 初始化审核状态
            if "review" not in draft:
                draft["review"] = {}
            if "生态环境" not in draft["review"]:
                draft["review"]["生态环境"] = ""
            # 检查是否已审核通过
            if "审核通过" in draft["review"]["生态环境"]:
                return draft["plan"]["生态环境"]
            
            print("开始规划生态环境保护方案\n")
            
            # 构建提示词
            prompt = f'''
    你是一位生态环境保护规划专家，任务是为{draft["village_name"]}村规划生态修复、污染治理和资源可持续利用方案。请按照以下要求完成规划：

    【任务目标】
    1. 分析生态环境的现状与优势（至少3个维度）。
    2. 识别生态环境保护中的关键问题（至少3个）。
    3. 提出生态环境保护方向与重点（至少3个方向）。
    4. 制定具体实施路径与优先级排序。
    5. 评估方案的可行性和潜在风险。

    【分析框架】
    1. **现状分析**：
    - 生态资源：森林、水资源、生物多样性等现状。
    - 污染状况：水、气、土壤污染现状与主要污染源。
    - 保护措施：现有生态保护政策与实施效果。
    - 资源利用：自然资源利用效率与可持续性。

    2. **问题诊断**：
    - 生态系统脆弱性：关键生态系统的退化程度。
    - 污染治理短板：现有治理措施的不足与改进空间。
    - 资源利用效率：资源浪费与低效利用问题。
    - 公众参与：村民生态保护意识与参与度。

    3. **发展方向建议**：
    - 生态修复：森林、湿地等生态系统修复的具体建议。
    - 污染治理：水、气、土壤污染治理的创新路径。
    - 资源循环利用：推动资源高效利用的具体措施。
    - 生态经济融合：将生态保护与产业发展结合的策略。

    4. **实施规划**：
    - 短期（1-2年）：快速见效的污染治理和生态修复项目。
    - 中期（3-5年）：技术引入、生态教育和资源循环利用体系构建。
    - 长期（5-10年）：生态系统全面恢复与生态经济融合发展。

    5. **可行性评估**：
    - 分析方案的实施成本、资源需求和技术可行性。
    - 提出潜在风险及其应对措施。

    【约束条件】
    - 成本可控：总投入不超过地方财政预算的15%。
    - 政策合规：建议需与国家和地方生态环境政策保持一致。
    - 技术可及：建议需基于区域可获取的技术资源。
    - 公众参与：建议需考虑村民接受度和参与度。
    - 生态效益：方案需确保长期生态效益最大化。

    【输出规范】
    - 使用分点结构，避免长段落。
    - 每项建议需包含：
    - 措施名称
    - 具体内容
    - 实施优先级（高/中/低）
    - 预期效果与风险评估
    - 成本估算与资金来源
    - 提供总结性建议，明确推荐方向
    输出的时候不要把报告审查结果加进去

    【上下文信息】
    村庄基本信息：{draft["document"]}
    中央政策文件：《数字乡村发展战略纲要》、《数字乡村发展行动计划（2022-2025年）》
    历史规划：{draft["plan"]["生态环境"] if "plan" in draft and "生态环境" in draft["plan"] else "无历史规划"}
    审核意见：{draft["review"]["生态环境"] if "review" in draft and "生态环境" in draft["review"] else "无审核意见"}
    已有信息：{draft["plan"] if "plan" in draft else "暂无已有规划"}

    【参考案例】
    成功案例：《浙江省数字乡村生态环境保护规划》提出的生态修复与污染治理路径
    政策支持：相关财政补贴、税收优惠和金融创新产品案例

    请按照上述要求完成规划，并确保建议具有可落地性。'''
            
            try:
                # 调用模型
                response = await call_model(self.semaphore, prompt, draft["model"])
                print("生态环境保护规划完成\n")
                return response.choices[0].message.content
            except Exception as e:
                print(f"生态环境保护规划时出错：{e}")
                return {"task": "ecological_protection_planning", "error": str(e)}
    
    async def brand_building(self, draft: rural_DraftState) -> Dict[str, Any]:
        """
        规划品牌建设方案，提升地方特色产品与服务的市场竞争力。
        
        :param draft: rural_DraftState 实例
        :return: 品牌建设规划结果（JSON 格式）
        """
        async with self.semaphore:
            # 初始化审核状态
            if "review" not in draft:
                draft["review"] = {}
            if "品牌建设" not in draft["review"]:
                draft["review"]["品牌建设"] = ""
            # 检查是否已审核通过
            if "审核通过" in draft["review"]["品牌建设"]:
                return draft["plan"]["品牌建设"]
            
            print("开始规划品牌建设方案\n")
            
            # 构建提示词
            prompt = f'''
    你是一位品牌建设规划专家，任务是为{draft["village_name"]}村规划品牌建设方案。请按照以下要求完成规划：

    【任务目标】
    1. 分析品牌建设的现状与优势（至少3个维度）。
    2. 识别品牌建设中的关键问题（至少3个）。
    3. 提出品牌建设方向与重点（至少3个方向）。
    4. 制定具体实施路径与优先级排序。
    5. 评估方案的可行性和潜在风险。

    【分析框架】
    1. **现状分析**：
    - 品牌认知度：现有品牌在市场中的知名度与影响力。
    - 品牌资产：品牌价值、声誉与消费者忠诚度。
    - 品牌传播：现有传播渠道与效果。
    - 产品特性：地方特色产品的独特性与市场定位。

    2. **问题诊断**：
    - 品牌定位模糊：品牌核心价值与目标市场不明确。
    - 传播效果不足：现有传播手段的覆盖范围与影响力有限。
    - 品牌管理薄弱：品牌维护与更新机制不完善。
    - 市场竞争压力：品牌差异化不足导致的市场竞争问题。

    3. **发展方向建议**：
    - 品牌定位优化：明确品牌核心价值与目标市场的具体建议。
    - 传播渠道拓展：利用数字技术提升品牌传播效率的路径。
    - 品牌资产管理：建立品牌维护与更新机制的具体措施。
    - 品牌与产业融合：将品牌建设与地方产业发展结合的策略。

    4. **实施规划**：
    - 短期（1-2年）：快速提升品牌认知度的基础建设与传播项目。
    - 中期（3-5年）：品牌传播体系完善与品牌资产管理机制建立。
    - 长期（5-10年）：品牌生态形成与市场竞争力全面提升。

    5. **可行性评估**：
    - 分析方案的实施成本、资源需求和技术可行性。
    - 提出潜在风险及其应对措施。

    【约束条件】
    - 成本可控：总投入不超过地方财政预算的10%。
    - 政策合规：建议需与国家和地方品牌建设政策保持一致。
    - 技术可及：建议需基于区域可获取的技术资源。
    - 公众参与：建议需考虑村民接受度和参与度。
    - 市场导向：品牌建设需以市场需求为核心。

    【输出规范】
    - 使用分点结构，避免长段落。
    - 每项建议需包含：
    - 措施名称
    - 具体内容
    - 实施优先级（高/中/低）
    - 预期效果与风险评估
    - 成本估算与资金来源
    - 提供总结性建议，明确推荐方向
    输出的时候不要把报告审查结果加进去

    【上下文信息】
    村庄基本信息：{draft["document"]}
    中央政策文件：《数字乡村发展战略纲要》、《数字乡村发展行动计划（2022-2025年）》
    历史规划：{draft["plan"]["品牌建设"] if "plan" in draft and "品牌建设" in draft["plan"] else "无历史规划"}
    审核意见：{draft["review"]["品牌建设"] if "review" in draft and "品牌建设" in draft["review"] else "无审核意见"}
    已有信息：{draft["plan"] if "plan" in draft else "暂无已有规划"}

    【参考案例】
    成功案例：《浙江省数字乡村品牌建设规划》提出的区域品牌数字化传播路径
    政策支持：相关财政补贴、税收优惠和金融创新产品案例

    请按照上述要求完成规划，并确保建议具有可落地性。'''
            
            try:
                # 调用模型
                response = await call_model(self.semaphore, prompt, draft["model"])
                print("品牌建设规划完成\n")
                return response.choices[0].message.content
            except Exception as e:
                print(f"品牌建设规划时出错：{e}")
                return {"task": "brand_building_planning", "error": str(e)}

    async def marketing_promotion(self, draft: rural_DraftState) -> Dict[str, Any]:
        """
        规划市场推广和营销方案，提升地方特色产品与服务的市场竞争力。
        
        :param draft: rural_DraftState 实例
        :return: 市场推广和营销规划结果（JSON 格式）
        """
        async with self.semaphore:
            # 初始化审核状态
            if "review" not in draft:
                draft["review"] = {}
            if "市场推广" not in draft["review"]:
                draft["review"]["市场推广"] = ""
            # 检查是否已审核通过
            if "审核通过" in draft["review"]["市场推广"]:
                return draft["plan"]["市场推广"]
            
            print("开始规划市场推广和营销方案\n")
            
            # 构建提示词
            prompt = f'''
    你是一位市场推广和营销规划专家，任务是为{draft["village_name"]}村规划市场推广和营销方案。请按照以下要求完成规划：

    【任务目标】
    1. 分析市场推广和营销的现状与优势（至少3个维度）。
    2. 识别市场推广和营销中的关键问题（至少3个）。
    3. 提出市场推广和营销方向与重点（至少3个方向）。
    4. 制定具体实施路径与优先级排序。
    5. 评估方案的可行性和潜在风险。

    【分析框架】
    1. **现状分析**：
    - 市场定位：现有产品与服务的市场定位与目标客户群体。
    - 推广渠道：现有推广渠道的覆盖范围与效果。
    - 营销活动：现有营销活动的类型与效果。
    - 竞争态势：主要竞争对手的市场策略与优势。

    2. **问题诊断**：
    - 市场定位模糊：产品与服务的核心价值与目标市场不明确。
    - 推广效果不足：现有推广手段的覆盖范围与影响力有限。
    - 营销活动单一：营销活动缺乏创新与多样性。
    - 数据支持薄弱：市场数据收集与分析能力不足。

    3. **发展方向建议**：
    - 市场定位优化：明确产品与服务的核心价值与目标市场的具体建议。
    - 推广渠道拓展：利用数字技术提升推广效率的路径。
    - 营销活动创新：设计多样化的营销活动提升市场影响力。
    - 数据驱动决策：建立市场数据收集与分析机制的具体措施。

    4. **实施规划**：
    - 短期（1-2年）：快速提升市场认知度的基础建设与推广项目。
    - 中期（3-5年）：推广体系完善与营销活动多样化。
    - 长期（5-10年）：市场生态形成与品牌影响力全面提升。

    5. **可行性评估**：
    - 分析方案的实施成本、资源需求和技术可行性。
    - 提出潜在风险及其应对措施。

    【约束条件】
    - 成本可控：总投入不超过地方财政预算的10%。
    - 政策合规：建议需与国家和地方市场推广政策保持一致。
    - 技术可及：建议需基于区域可获取的技术资源。
    - 公众参与：建议需考虑村民接受度和参与度。
    - 市场导向：推广和营销需以市场需求为核心。

    【输出规范】
    - 使用分点结构，避免长段落。
    - 每项建议需包含：
    - 措施名称
    - 具体内容
    - 实施优先级（高/中/低）
    - 预期效果与风险评估
    - 成本估算与资金来源
    - 提供总结性建议，明确推荐方向
    输出的时候不要把报告审查结果加进去

    【上下文信息】
    村庄基本信息：{draft["document"]}
    中央政策文件：《数字乡村发展战略纲要》、《数字乡村发展行动计划（2022-2025年）》
    历史规划：{draft["plan"]["市场推广"] if "plan" in draft and "市场推广" in draft["plan"] else "无历史规划"}
    审核意见：{draft["review"]["市场推广"] if "review" in draft and "市场推广" in draft["review"] else "无审核意见"}
    已有信息：{draft["plan"] if "plan" in draft else "暂无已有规划"}

    【参考案例】
    成功案例：《浙江省数字乡村市场推广规划》提出的数字化营销路径
    政策支持：相关财政补贴、税收优惠和金融创新产品案例

    请按照上述要求完成规划，并确保建议具有可落地性。'''
            
            try:
                # 调用模型
                response = await call_model(self.semaphore, prompt, draft["model"])
                print("市场推广和营销规划完成\n")
                return response.choices[0].message.content
            except Exception as e:
                print(f"市场推广和营销规划时出错：{e}")
                return {"task": "marketing_promotion_planning", "error": str(e)}
            
    async def monitoring_evaluation(self, draft: rural_DraftState) -> Dict[str, Any]:
        """
        规划监测评估体系，确保数字乡村建设项目的实施效果与长期效益。
        
        :param draft: rural_DraftState 实例
        :return: 监测评估规划结果（JSON 格式）
        """
        async with self.semaphore:
            # 初始化审核状态
            if "review" not in draft:
                draft["review"] = {}
            if "监测评估" not in draft["review"]:
                draft["review"]["监测评估"] = ""
            # 检查是否已审核通过
            if "审核通过" in draft["review"]["监测评估"]:
                return draft["plan"]["监测评估"]
            
            print("开始规划监测评估体系\n")
            
            # 构建提示词
            prompt = f'''
    你是一位监测评估体系规划专家，任务是为{draft["village_name"]}村规划监测评估体系。请按照以下要求完成规划：

    【任务目标】
    1. 分析现有监测评估体系的现状与优势（至少3个维度）。
    2. 识别监测评估体系中的关键问题（至少3个）。
    3. 提出监测评估体系优化方向与重点（至少3个方向）。
    4. 制定具体实施路径与优先级排序。
    5. 评估方案的可行性和潜在风险。

    【分析框架】
    1. **现状分析**：
    - 监测指标：现有监测指标的覆盖范围与科学性。
    - 评估方法：现有评估方法的适用性与准确性。
    - 数据收集：数据收集的渠道、频率与质量。
    - 反馈机制：监测结果如何用于项目调整与优化。

    2. **问题诊断**：
    - 指标体系不完善：关键指标缺失或指标设计不合理。
    - 数据质量不足：数据准确性、及时性与完整性问题。
    - 评估方法单一：缺乏多样化的评估手段。
    - 反馈机制薄弱：监测结果未能有效指导项目调整。

    3. **发展方向建议**：
    - 指标体系优化：设计科学、全面的监测指标体系。
    - 数据收集增强：利用数字技术提升数据收集效率与质量。
    - 多元评估方法：引入多种评估手段确保评估结果的可靠性。
    - 动态反馈机制：建立监测结果与项目调整的闭环机制。

    4. **实施规划**：
    - 短期（1-2年）：快速建立基础监测体系与数据收集机制。
    - 中期（3-5年）：完善指标体系与评估方法，建立反馈机制。
    - 长期（5-10年）：形成全面、动态的监测评估体系，确保项目持续优化。

    5. **可行性评估**：
    - 分析方案的实施成本、资源需求和技术可行性。
    - 提出潜在风险及其应对措施。

    【约束条件】
    - 成本可控：总投入不超过地方财政预算的5%。
    - 政策合规：建议需与国家和地方监测评估政策保持一致。
    - 技术可及：建议需基于区域可获取的技术资源。
    - 公众参与：建议需考虑村民接受度和参与度。
    - 数据安全：监测数据需符合隐私保护与数据安全要求。

    【输出规范】
    - 使用分点结构，避免长段落。
    - 每项建议需包含：
    - 措施名称
    - 具体内容
    - 实施优先级（高/中/低）
    - 预期效果与风险评估
    - 成本估算与资金来源
    - 提供总结性建议，明确推荐方向
    输出的时候不要把报告审查结果加进去

    【上下文信息】
    村庄基本信息：{draft["document"]}
    中央政策文件：《数字乡村发展战略纲要》、《数字乡村发展行动计划（2022-2025年）》
    历史规划：{draft["plan"]["监测评估"] if "plan" in draft and "监测评估" in draft["plan"] else "无历史规划"}
    审核意见：{draft["review"]["监测评估"] if "review" in draft and "监测评估" in draft["review"] else "无审核意见"}
    已有信息：{draft["plan"] if "plan" in draft else "暂无已有规划"}

    【参考案例】
    成功案例：《浙江省数字乡村监测评估体系规划》提出的动态监测与反馈机制
    政策支持：相关财政补贴、技术指导和数据安全法规案例

    请按照上述要求完成规划，并确保建议具有可落地性。'''
            
            try:
                # 调用模型
                response = await call_model(self.semaphore, prompt, draft["model"])
                print("监测评估体系规划完成\n")
                return response.choices[0].message.content
            except Exception as e:
                print(f"监测评估体系规划时出错：{e}")
                return {"task": "monitoring_evaluation_planning", "error": str(e)}
            
    async def policy_funding_support(self, draft: rural_DraftState) -> Dict[str, Any]:
        """
        规划政策支持与资金保障方案，确保数字乡村建设项目的顺利实施。
        
        :param draft: rural_DraftState 实例
        :return: 政策支持与资金保障规划结果（JSON 格式）
        """
        async with self.semaphore:
            # 初始化审核状态
            if "review" not in draft:
                draft["review"] = {}
            if "政策资金支持" not in draft["review"]:
                draft["review"]["政策资金支持"] = ""
            # 检查是否已审核通过
            if "审核通过" in draft["review"]["政策资金支持"]:
                return draft["plan"]["政策资金支持"]
            
            print("开始规划政策支持与资金保障方案\n")
            
            # 构建提示词
            prompt = f'''
    你是一位政策与资金规划专家，任务是为{draft["village_name"]}村规划政策支持与资金保障方案。请按照以下要求完成规划：

    【任务目标】
    1. 分析现有政策支持与资金保障的现状与优势（至少3个维度）。
    2. 识别政策支持与资金保障中的关键问题（至少3个）。
    3. 提出政策支持与资金保障优化方向与重点（至少3个方向）。
    4. 制定具体实施路径与优先级排序。
    5. 评估方案的可行性和潜在风险。

    【分析框架】
    1. **现状分析**：
    - 政策支持：现有政策的覆盖范围、执行效果与支持力度。
    - 资金来源：资金的主要来源、分配机制与使用效率。
    - 项目匹配：政策与资金支持与项目需求的匹配度。
    - 制度保障：资金管理与政策执行的制度保障情况。

    2. **问题诊断**：
    - 政策执行不到位：政策落实过程中存在的障碍与问题。
    - 资金缺口：现有资金无法满足项目需求的具体问题。
    - 资金使用效率低：资金分配与使用中的浪费与低效问题。
    - 制度不完善：资金管理与政策执行缺乏有效监督与评估。

    3. **发展方向建议**：
    - 政策创新：设计更符合地方需求的政策支持体系。
    - 资金整合：优化资金来源与分配机制，提高资金使用效率。
    - 制度完善：建立资金管理与政策执行的监督与评估机制。
    - 多元化支持：探索社会资本引入与公私合作模式。

    4. **实施规划**：
    - 短期（1-2年）：快速建立基础政策支持与资金保障机制。
    - 中期（3-5年）：完善政策体系与资金分配机制，提高执行效率。
    - 长期（5-10年）：形成全面、可持续的政策支持与资金保障体系。

    5. **可行性评估**：
    - 分析方案的实施成本、资源需求和技术可行性。
    - 提出潜在风险及其应对措施。

    【约束条件】
    - 成本可控：建议需确保资金使用效率最大化，避免浪费。
    - 政策合规：建议需与国家和地方相关政策保持一致。
    - 公众参与：建议需考虑村民接受度和参与度。
    - 风险可控：方案需确保资金安全与政策执行效果。
    - 可持续性：建议需确保长期资金支持与政策稳定性。

    【输出规范】
    - 使用分点结构，避免长段落。
    - 每项建议需包含：
    - 措施名称
    - 具体内容
    - 实施优先级（高/中/低）
    - 预期效果与风险评估
    - 成本估算与资金来源
    - 提供总结性建议，明确推荐方向
    输出的时候不要把报告审查结果加进去

    【上下文信息】
    村庄基本信息：{draft["document"]}
    中央政策文件：《数字乡村发展战略纲要》、《数字乡村发展行动计划（2022-2025年）》
    历史规划：{draft["plan"]["政策资金支持"] if "plan" in draft and "政策资金支持" in draft["plan"] else "无历史规划"}
    审核意见：{draft["review"]["政策资金支持"] if "review" in draft and "政策资金支持" in draft["review"] else "无审核意见"}
    已有信息：{draft["plan"] if "plan" in draft else "暂无已有规划"}

    【参考案例】
    成功案例：《江苏省数字乡村政策支持与资金保障规划》提出的多元化资金整合路径
    政策支持：相关财政补贴、税收优惠和金融创新产品案例

    请按照上述要求完成规划，并确保建议具有可落地性。'''
            
            try:
                # 调用模型
                response = await call_model(self.semaphore, prompt, draft["model"])
                print("政策支持与资金保障规划完成\n")
                return response.choices[0].message.content
            except Exception as e:
                print(f"政策支持与资金保障规划时出错：{e}")
                return {"task": "policy_funding_support_planning", "error": str(e)}
        
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
                self.industry_positioning(draft),
                self.industry_development(draft),
                self.industry_system(draft),
                self.primary_industry_planning(draft),
                self.secondary_industry_planning(draft),
                self.tertiary_industry_planning(draft),
                self.infrastructure_planning(draft),
                self.ecological_protection(draft),
                self.brand_building(draft),
                self.marketing_promotion(draft),
                self.monitoring_evaluation(draft),
                self.policy_funding_support(draft),
        ]

        results = await asyncio.gather(*tasks)


        # 合并结果到 draft 中
        if "plan" not in draft:
            draft["plan"] = {}
        
        # 将字典的键转换为列表
        keys = list(self.planning_tasks.keys())
        k=0
        for result in results:
            try:
                if keys[k] not in draft["plan"]:
                    draft["plan"][keys[k]] = {}
                draft["plan"][keys[k]] = result
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

    save_dict_to_file(result_draft["plan"], "Results", f"{result_draft["village_name"]}乡村振兴规划报告", "markdown")