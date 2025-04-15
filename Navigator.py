import asyncio
import time  # 添加时间模块用于重试间隔
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
import ast
import json

from memory.draft import rural_DraftState

from dotenv import load_dotenv
load_dotenv()

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
        self.local_condition = draft["document"]
        self.model=draft["model"]


        # 第一轮对话：分析市场空白
        market_gaps = await self._analyze_market_gaps()
        self.conversation_history.append({"role": "assistant", "content": f"市场空白分析：{market_gaps} ###"})

        # 第二轮对话：分析成功案例（包含幸存者偏差分析）
        success_cases = await self._analyze_success_cases(market_gaps)
        self.conversation_history.append({"role": "assistant", "content": f"成功案例与幸存者偏差分析：{success_cases} ###"})

        # 第四轮对话：分析风险
        risks = await self._analyze_risks(success_cases)
        self.conversation_history.append({"role": "assistant", "content": f"风险分析：{risks} ###"})

        # 第五轮对话：确定发展定位
        development_positions = await self._determine_development_positions()
        if development_positions:
            draft["navigate"]=development_positions
            draft["navigate_analysis"]=self.conversation_history

        return draft

    async def _call_model_with_retry(self, prompt: str, retries: int = 3, delay: int = 1) -> str:
        """
        调用大模型并添加重试机制。

        :param prompt: 提示内容
        :param retries: 最大重试次数
        :param delay: 每次重试之间的延迟时间（秒）
        :return: 大模型返回的内容
        """
        for attempt in range(retries):
            try:
                response = await ChatOpenAI(model_name=self.model).ainvoke([{"role": "user", "content": prompt}])
                return response.content
            except Exception as e:
                print(f"调用大模型失败（尝试 {attempt + 1}/{retries}）：{e}")
                if attempt < retries - 1:
                    time.sleep(delay)  # 等待一段时间后重试
                else:
                    print("多次尝试后仍然失败，返回空结果。")
                    return "调用失败：无法获取结果。"

    async def _analyze_market_gaps(self) -> str:
        """
        分析市场空白。

        :return: 市场空白分析结果
        """
        prompt = f'''
根据以下信息，分析 {self.village_name} 的市场空白：

### 输入信息
1. **村庄现状**：
{self.local_condition}

### 分析要求
1. **市场需求**：
   - 分析当前市场的主要需求是什么。
   - 提供具体数据支撑（如市场规模、增长率等）。

2. **竞争分析**：
   - 分析当前市场的主要竞争者及其优势。
   - 提供具体数据支撑（如市场份额、竞争者数量等）。

3. **市场空白**：
   - 分析 {self.village_name} 是否存在未被满足的市场需求。
   - 提供具体数据支撑（如未被满足的需求规模、潜在客户数量等）。

4. **建议**：
   - 提供针对 {self.village_name} 的市场定位建议。
   - 提供具体数据支撑（如目标客户群体、市场进入策略等）。

请基于以上要求，提供详细的市场空白分析报告，并附上具体数据和逻辑推导过程。
'''
        print("开始分析市场空白...")
        return await self._call_model_with_retry(prompt)

    async def _analyze_success_cases(self, market_gaps: str) -> str:
        """
        分析类似村庄的成功案例并评估幸存者偏差。

        :param market_gaps: 市场空白分析结果
        :return: 成功案例分析结果（包含幸存者偏差分析）
        """
        prompt = f'''
根据以下信息，分析类似村庄的成功案例，并评估是否存在幸存者偏差：

### 第一部分：成功案例分析
1. **市场空白分析结果**：
   - 市场空白分析结果：{market_gaps}
   - 村庄现状：{self.local_condition}

2. **案例要求**：
   - 列出与 {self.village_name} 具有相似资源条件和市场环境的村庄成功案例。
   - 提供案例的来源（如研究报告、政府文件、新闻报道等）和链接。

3. **案例分析**：
   - **成功经验**：该案例村的成功经验是什么？具体的做法和策略有哪些？
   - **相似性**：该村与 {self.village_name} 的相似之处是什么？提供具体数据（如资源条件、市场需求等）作为支撑。
   - **差异性**：该村与 {self.village_name} 的不同之处是什么？提供具体数据（如政策支持、基础设施等）作为支撑。
   - **可复制性**：该村的成功经验能否在 {self.village_name} 复制？需要哪些条件？提供具体数据支撑。
   - **资源利用**：该村是如何发挥资源优势的？提供具体数据（如土地利用率、政策补贴金额等）。
   - **劣势克服**：该村是如何克服资源劣势的？提供具体数据（如资金投入、技术支持等）。

### 第二部分：幸存者偏差分析
1. **偏差评估**：
   - 分析上述成功案例是否存在幸存者偏差。
   - 提供更多失败案例及其原因，确保分析的全面性。

2. **失败案例要求**：
   - 列出与 {self.village_name} 条件相似但未能成功的村庄案例。
   - 提供失败案例的来源和链接。

3. **失败案例分析**：
   - **失败原因**：这些失败案例的主要问题是什么？提供具体数据支撑。
   - **可避免性**：这些失败案例的问题能否避免？需要采取哪些措施？
   - **代表性**：这些失败案例和成功案例哪个更具有代表性？哪个是个别情况，哪个是普遍情况？

4. **总结**：
   - 综合成功案例和失败案例，分析 {self.village_name} 应该优先关注的关键因素。
   - 提供具体建议，帮助规避潜在风险并提高成功概率。

请基于以上要求，提供详细的分析报告，并附上具体数据和逻辑推导过程。
'''
        print("开始分析成功案例...")
        return await self._call_model_with_retry(prompt)

    async def _analyze_risks(self, success_cases_analysis: str) -> str:
        """
        分析村庄发展可能面临的风险。

        :param success_cases_analysis: 成功案例与幸存者偏差分析结果
        :return: 风险分析结果
        """
        prompt = f'''
    基于以下信息，全面分析 {self.village_name} 在发展过程中可能面临的风险，并提供详细的风险评估报告：

    ### 输入信息
    1. **成功案例与幸存者偏差分析结果**：
    {success_cases_analysis}

    2. **村庄现状**：
    {self.local_condition}

    ### 风险分析要求
    1. **风险识别**：
    - 列出 {self.village_name} 在发展过程中可能面临的主要风险，包括但不限于以下方面：
        - 自然风险（如气候变化、自然灾害等）。
        - 市场风险（如市场需求波动、竞争加剧等）。
        - 资源风险（如资源枯竭、土地利用冲突等）。
        - 政策风险（如政策变动、补贴减少等）。
        - 技术风险（如技术落后、技术依赖等）。
        - 社会风险（如人口流失、劳动力不足等）。

    2. **风险评估**：
    - 对每个风险进行详细评估，回答以下问题：
        - **可能性**：该风险发生的概率有多大？提供具体数据支撑。
        - **主要问题**：该风险的核心问题是什么？提供具体数据支撑。
        - **主要影响**：该风险可能对 {self.village_name} 的发展造成哪些影响？提供具体数据支撑。

    3. **风险应对措施**：
    - 针对每个风险，提出可行的应对措施，回答以下问题：
        - **应对策略**：有哪些具体的应对策略？提供详细说明。
        - **资源需求**：实施这些策略需要哪些资源（如资金、技术、政策支持等）？
        - **可行性**：这些应对措施的可行性有多大？提供具体数据支撑。

    4. **优先级排序**：
    - 根据风险的严重性和可控性，对所有风险进行优先级排序，明确哪些风险需要优先解决。

    5. **总结与建议**：
    - 综合以上分析，提供一份总结报告，明确 {self.village_name} 在发展过程中需要重点关注的风险及其应对策略。

    请基于以上要求，提供详细的风险分析报告，并附上具体数据和逻辑推导过程。
    '''
        print("开始分析风险...")
        return await self._call_model_with_retry(prompt)

    async def _determine_development_positions(self) -> str:
        """
        确定村庄的发展定位。

        :return: 发展定位建议
        """
        prompt = f'''
基于以下信息，确定 {self.village_name} 的发展定位：

### 输入信息
1. **村庄现状**：
{self.local_condition}

2. **市场空白分析**：
{self.conversation_history[0]["content"]}

3. **成功案例与幸存者偏差分析**：
{self.conversation_history[1]["content"]}

4. **风险分析**：
{self.conversation_history[2]["content"]}

### 分析要求
1. **发展方向**：
   - 提出 {self.village_name} 的主要发展方向。
   - 提供具体数据支撑（如资源优势、市场需求等）。

2. **发展目标**：
   - 提出 {self.village_name} 的短期和长期发展目标。
   - 提供具体数据支撑（如经济指标、社会指标等）。

3. **发展策略**：
   - 提出实现发展目标的具体策略。
   - 提供具体数据支撑（如政策支持、资金需求等）。

4. **可行性分析**：
   - 分析提出的发展方向和策略的可行性。
   - 提供具体数据支撑（如资源可用性、政策支持等）。

请基于以上要求，提供详细的发展定位建议，并附上具体数据和逻辑推导过程。
'''
        print("开始分析发展定位...")
        return await self._call_model_with_retry(prompt)

if __name__=="__main__":
    # 创建 rural_DraftState 实例
    draft = rural_DraftState(
        draft=[],
        village_name="金田村",
        model="google/gemini-2.0-flash-001",
        document="""
                金田村自然环境很好。
                """,
        navigate={},
        navigate_analysis=[]
    )

    # 初始化规划智能体
    navigator = Navigator()

    # 运行规划流程
    planning_draft = asyncio.run(navigator.start_planning(draft=draft))
    print(planning_draft["navigate"])