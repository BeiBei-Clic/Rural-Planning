import asyncio
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
import re

from memory.draft import rural_DraftState

import os
from dotenv import load_dotenv
load_dotenv()
# print("OPENAI_BASE_URL:", os.getenv("OPENAI_BASE_URL"))
# print("OPENAI_API_KEY:", os.getenv("OPENAI_API_KEY"))


class Navigator:
    """
    乡村发展定位规划智能体，通过多轮对话引导智能体进行思考，确定村庄的发展定位。
    """

    def __init__(self):
        """
        初始化乡村发展定位规划智能体。
        """
        self.conversation_history = []

    async def start_planning(self, draft: rural_DraftState) -> Dict[str, Any]:
        """
        开始规划流程，通过多轮对话确定村庄的发展定位。

        :param draft: rural_DraftState 实例，包含村庄名称和现状信息
        :return: 包含发展定位建议的字典
        """
        print(f"开始规划 {draft['village_name']} 的发展定位...")
        self.village_name = draft["village_name"]
        self.local_condition = draft["local_condition"]
        self.model=draft["model"]
        

        # 第一轮对话：分析市场空白
        market_gaps = await self._analyze_market_gaps()
        self.conversation_history.append({"role": "assistant", "content": f"市场空白分析：{market_gaps} ###"})

        # 第二轮对话：分析成功案例
        success_cases = await self._analyze_success_cases(market_gaps)
        self.conversation_history.append({"role": "assistant", "content": f"成功案例分析：{success_cases} ###"})

        # 第三轮对话：分析幸存者偏差
        survivor_bias = await self._analyze_survivor_bias(success_cases)
        self.conversation_history.append({"role": "assistant", "content": f"幸存者偏差分析：{survivor_bias} ###"})

        # 第四轮对话：分析风险
        risks = await self._analyze_risks(survivor_bias)
        self.conversation_history.append({"role": "assistant", "content": f"风险分析：{risks} ###"})

        # 第五轮对话：确定发展定位
        development_positions = await self._determine_development_positions()
        if development_positions:
            draft["navigate"].update(development_positions)

        return draft

    async def _analyze_market_gaps(self) -> str:
        """
        分析村庄所处环境的市场空白。

        :return: 市场空白分析结果
        """
        prompt = f'''
根据 {self.village_name} 的资源和区位优势，分析当前市场环境中可能存在的市场空白：
{self.local_condition}
具体分析{self.village_name}的市场空白，给出具体数字作为支撑：
{self.village_name}有什么优势条件，给出具体数字，
{self.village_name}所处地方有什么市场需求，给出具体数字，
该市场需求现在的提供者有谁，给出具体单位，他能提供多少，给出具体数字，
减去这些提供者后，该市场需求还有多少空白，给出具体数字，
与该提供者进行竞争，{self.village_name}有什么竞争优势，给出具体数字，
{self.village_name}有什么竞争劣势，给出具体数字。
'''
        try:
            response = await ChatOpenAI(model_name=self.model).ainvoke([{"role": "user", "content": prompt}])
        except Exception as e:
            print(f"Error in _analyze_market_gaps: {e}")
            return ""
        return response.content

    async def _analyze_success_cases(self, market_gaps: str) -> str:
        """
        分析类似村庄的成功案例。

        :param market_gaps: 市场空白分析结果
        :return: 成功案例分析结果
        """
        prompt = f'''
根据 {self.village_name} 的市场空白分析结果，分析类似村庄在相关方向上的成功案例，并总结成功经验：
市场空白分析结果：{market_gaps}
村庄现状：{self.local_condition}
该案例必须是真实的，给出你获取该信息的渠道和链接。
该案例村的成功经验是什么？
该村与{self.village_name}的相似之处是什么？给出具体数字作为支撑。
该村与{self.village_name}的不同之处是什么？给出具体数字作为支撑。
该村的成功经验能否在{self.village_name}村复制？给出具体数字作为支撑。
该村的成功之路上是如何发挥资源优势的？给出具体数字作为支撑。
该村的成功之路上是如何克服资源劣势的？给出具体数字作为支撑。
'''
        try:
            response = await ChatOpenAI(model_name=self.model).ainvoke([{"role": "user", "content": prompt}])
        except Exception as e:
            print(f"Error in _analyze_success_cases: {e}")
            return ""
        return response.content

    async def _analyze_survivor_bias(self, success_cases: str) -> str:
        """
        分析成功案例是否存在幸存者偏差。

        :param success_cases: 成功案例分析结果
        :return: 幸存者偏差分析结果
        """
        prompt = f'''
分析上述成功案例是否存在幸存者偏差，并提供更多的失败案例及其原因：
成功案例分析结果：{success_cases}
村庄现状：{self.local_condition}
案例必须真实的，给出来源文件和链接。
该失败案例的问题能否避免，给出具体数字作为支撑。
这些失败案例和成功案例哪个才更具有代表性，哪个是个别情况，哪个是普遍情况。
'''
        try:
            response = await ChatOpenAI(model_name=self.model).ainvoke([{"role": "user", "content": prompt}])
        except Exception as e:
            print(f"Error in _analyze_survivor_bias: {e}")
            return ""
        return response.content

    async def _analyze_risks(self, survivor_bias: str) -> str:
        """
        分析村庄发展可能面临的风险。

        :param survivor_bias: 幸存者偏差分析结果
        :return: 风险分析结果
        """
        prompt = f'''
从失败案例中吸取教训，分析 {self.village_name} 在发展过程中可能面临的风险：
幸存者偏差分析结果：{survivor_bias}
村庄现状：{self.local_condition}
该风险的可能性有多大，给出具体数字作为支撑。
该风险的主要问题是什么？给出具体数字作为支撑。
该风险的主要影响是什么？给出具体数字作为支撑。
该风险的主要应对措施是什么？给出具体数字作为支撑。
该风险的主要应对措施的可行性有多大，给出具体数字作为支撑。
'''
        try:
            response = await ChatOpenAI(model_name=self.model).ainvoke([{"role": "user", "content": prompt}])
        except Exception as e:
            print(f"Error in _analyze_risks: {e}")
            return ""
        return response.content

    async def _determine_development_positions(self) -> Dict[str, Dict[str, str]]:
        """
        确定村庄的发展定位。

        :return: 发展定位建议字典
        """
        prompt = f'''
综合以上分析，为 {self.village_name} 确定几个切实可行的发展定位：
综合分析结果：{self.conversation_history}
村庄现状：{self.local_condition}
要参考市场空白、成功案例、幸存者偏差和风险分析，给出具体数字作为支撑。
你的返回应该是这样的：
发展定位1：xxxx
发展定位1的具体分析：
- 市场空白：xxxx,具体的数字支撑是什么
- 成功案例：xxxx，具体的案例支撑是什么
- 大方向做法：xxxx，具体的的做法有哪些，做到什么程度，数据支撑是什么
- 风险分析：xxxx，具体的数据支撑是什么

发展定位2：xxxx
发展定位2的具体分析：
- 市场空白：xxxx,具体的数字支撑是什么
- 成功案例：xxxx，具体的案例支撑是什么
- 大方向做法：xxxx，具体的的做法有哪些，做到什么程度，数据支撑是什么
- 风险分析：xxxx，具体的数据支撑是什么

发展定位3：...等等

把所有可能的发展定位都找出来

请严格按照上述格式返回内容。
'''
        try:
            response = await ChatOpenAI(model_name=self.model).ainvoke([{"role": "user", "content": prompt}])
        except Exception as e:
            print(f"Error in _determine_development_positions: {e}")
            return {}

        # 清理和解析响应内容
        cleaned_text = "\n".join(
            line for line in response.content.split('\n')
            if line.startswith("发展定位") or line.startswith("- ")
        )
        response_dict = text_to_dict(cleaned_text)

        return response_dict


def text_to_dict(text: str) -> Dict[str, List[str]]:
    """
    将文本内容转换为字典格式。

    :param text: 需要转换的文本内容
    :return: 转换后的字典
    """
    result = {}
    current_section = None
    lines = text.split('\n')
    for line in lines:
        line = line.strip().replace("：", ":").replace("，", ",").replace("。", ".")
        if line.startswith("发展定位"):
            # 提取发展定位名称
            match = re.match(r"发展定位\d+[:：](.+)", line)
            if match:
                current_section = match.group(1).strip()
                result[current_section] = []
        elif current_section and line.startswith("- "):
            # 提取分析内容
            analysis_content = line[2:].strip()  # 去掉"- "并去除多余空格
            if analysis_content:
                result[current_section].append(analysis_content)
        elif current_section and line.startswith("发展定位"):
            # 如果遇到新的发展定位，但当前section还未处理完，打印警告
            print(f"Warning: New development position found before finishing current section - {line}")
    return result


if __name__ == "__main__":
    # 创建 rural_DraftState 实例
    draft = rural_DraftState(
        draft=[],
        village_name="金田村",
        model="deepseek/deepseek-chat-v3-0324:free",
        local_condition={
            "natural": {
                "地形": "丘陵",
                "气候": "温和湿润",
                "水源": "丰富",
            },
            "policy": {
                "国家政策": "乡村振兴战略",
                "地方政策": "生态文明建设",
            },
        },
        navigate={},
    )

    # 初始化规划智能体
    navigator = Navigator()

    # 运行规划流程
    planning_draft = asyncio.run(navigator.start_planning(draft=draft))
    print(planning_draft["navigate"])