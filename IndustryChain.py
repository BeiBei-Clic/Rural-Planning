import asyncio
from typing import Dict, Any, List, Tuple
from langchain_openai import ChatOpenAI

from memory.draft import rural_DraftState
from guidelines import guidelines

from dotenv import load_dotenv
load_dotenv()


class IndustryChainAgent:
    """
    产业链分析智能体，用于分析核心产业的上下游产业链，并提出优化建议。
    """

    def __init__(self):
        """
        初始化产业链分析智能体。
        """
        self.chain_segments = {
            "upstream": "上游原材料供应，例如种子、肥料、农药等",
            "midstream": "中游生产加工，例如种植、采摘、初加工等",
            "downstream": "下游市场销售，例如包装、物流、销售等",
            "supporting_services": "配套服务，例如农业技术培训、农产品质量检测等"
        }

    async def analyze_segment(self, draft: rural_DraftState, segment: str) -> Dict[str, Any]:
        """
        分析单个产业链环节。

        :param draft: rural_DraftState 实例
        :param segment: 产业链环节（例如 upstream, midstream 等）
        :param description: 产业链环节的描述
        :return: 分析结果（JSON 格式）
        """
        print(f"开始分析产业链{segment}环节\n")
        # 构造提示信息
        prompt = f'''
请根据以下信息分析{draft["village_name"]}村的核心产业（{draft["local_condition"]["core_industry"]}）的{segment}环节，并提出优化建议：

**村庄基本信息**：{draft["document"]}和基本信息分析{draft["navigate_analysis"]}

**要求**：
- 分析该环节的现状和问题。
- 提出具体的优化建议。
- 请以 JSON 格式返回结果，格式如下：
  {{
    "segment": "{segment}",
    "current_status": "现状描述",
    "issues": "问题列表",
    "recommendations": "优化建议"
  }}
'''

        try:
            # 调用模型生成分析报告
            response = await ChatOpenAI(model_name=draft["model"]).ainvoke([{"role": "user", "content": prompt}])
            print(f"产业链{segment}环节分析完成")
            return response.content
        except Exception as e:
            print(f"分析 {segment} 环节时出错：{e}")
            return {"segment": segment, "error": str(e)}

    async def parallel_analyze_chains(self, draft: rural_DraftState) -> Dict[str, Any]:
        """
        并行分析核心产业的上下游产业链。

        :param draft: rural_DraftState 实例
        :return: 更新后的 draft_state，包含产业链分析结果和优化建议
        """
        print("开始并行分析产业链\n")
        tasks = []

        # 为每个产业链环节创建分析任务
        for segment, description in self.chain_segments.items():
            task = self.analyze_segment(draft, segment)
            tasks.append(task)

        # 并行执行所有任务
        results = await asyncio.gather(*tasks)

        # 合并结果到 draft 中
        if "industry_chain" not in draft:
            draft["industry_chain"] = {}
        draft["industry_chain"] = {result: result for result in results if "segment" in result}

        print("并行分析完成")
        return draft  # 返回最终的 draft_state

    @staticmethod
    def generate_industry_chain_report(draft: rural_DraftState) -> str:
        """
        生成产业链分析报告。

        :param draft: rural_DraftState 实例
        :return: 产业链分析报告的文本
        """
        if "industry_chain" not in draft or not draft["industry_chain"]:
            return "产业链分析结果为空，请先运行分析。"

        report = f"### {draft['village_name']}村产业链分析报告\n\n"
        report += f"**核心产业**: {draft['local_condition']['core_industry']}\n\n"

        for segment, analysis in draft["industry_chain"].items():
            report += f"#### {analysis['segment'].capitalize()} 分析\n"
            report += f"- **现状**: {analysis.get('current_status', '无描述')}\n"
            report += "- **问题**:\n"
            for issue in analysis.get("issues", []):
                report += f"  - {issue}\n"
            report += "- **优化建议**:\n"
            for recommendation in analysis.get("recommendations", []):
                report += f"  - {recommendation}\n\n"

        return report


if __name__ == "__main__":
    # 创建 rural_DraftState 实例
    draft = rural_DraftState(
        draft=[],
        document="""
                金田村自然环境很好，适合特色农产品种植。
                """,
        village_name="金田村",
        model="qwen/qwen2.5-vl-32b-instruct:free",
        local_condition={"natural": {}, "policy": {}, "core_industry": "特色农产品种植"},
        navigate={},
        navigate_analysis=[],
        industry_chain={}
    )

    # 初始化产业链分析智能体
    industry_chain_agent = IndustryChainAgent()

    # 并行分析产业链
    result_draft = asyncio.run(industry_chain_agent.parallel_analyze_chains(draft=draft))

    print(result_draft["industry_chain"])

    # # 生成并输出产业链分析报告
    # report = industry_chain_agent.generate_industry_chain_report(result_draft)
    # print(report)