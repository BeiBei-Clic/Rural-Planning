import asyncio
from typing import Dict, Any
import os

# 假设你已经定义了 rural_DraftState 和 call_model
from memory.draft import rural_DraftState
from Call_Model import call_model
from save_to_local import save_dict_to_file

class Reportor_2:
    def __init__(self, concurrency_limit=60):
        self.concurrency_limit = concurrency_limit
        self.semaphore = asyncio.Semaphore(concurrency_limit)

    async def report_in_batches(self, draft: Dict[str, Any], batch_size: int = 3) -> str:
        """
        分批提取 draft["plan"] 中的信息，并整合到一个完整的报告中。
        
        :param draft: rural_DraftState 实例
        :param batch_size: 每批提取的数量，默认为 3
        :return: 完整的报告内容
        """
        if "plan" not in draft or not isinstance(draft["plan"], dict):
            print("draft['plan'] 不存在或不是字典")
            return ""
        
        plan_dict = draft["plan"]
        keys = list(plan_dict.keys())
        total_items = len(keys)
        if total_items == 0:
            print("draft['plan'] 是空字典")
            return ""
        
        # 计算需要的批次数
        num_batches = (total_items + batch_size - 1) // batch_size
        
        result = ""
        
        for i in range(num_batches):
            start_idx = i * batch_size
            end_idx = min((i + 1) * batch_size, total_items)
            batch_keys = keys[start_idx:end_idx]
            
            # 将当前批次的键值对转换为字符串格式
            batch_str = "\n".join([f"{key}: {plan_dict[key]}" for key in batch_keys])
            
            # 构建提示词
            prompt = f'''
你是一位报告整合专家，任务是将以下内容整合到已有的报告中：

【已有报告内容】
{result}

【新内容】
{batch_str}

【要求】
1. 将新内容整合到已有报告中，确保报告结构清晰。
2. 使用分点结构，避免长段落。
3. 提供总结性建议，明确推荐方向
4. 输出的时候不要把报告审查结果加进去
5. 确保报告内容连贯，逻辑清晰'''

            try:
                # 调用模型
                response = await call_model(self.semaphore, prompt,"google/gemma-3-4b-it")
                result = response.choices[0].message.content
                print(f"第 {i+1} 批次信息提取完成")
            except Exception as e:
                print(f"第 {i+1} 批次信息提取时出错：{e}")
                result += f"\n【第 {i+1} 批次提取失败】: {str(e)}"
        
        return result

    async def generate_report(self, draft: rural_DraftState) -> Dict[str, Any]:
        """
        根据已有规划报告，生成综合报告。

        :param draft: rural_DraftState 实例
        :return: 综合报告（字典格式）
        """
        async with self.semaphore:
            save_dict_to_file(draft["plan"], "Results", f"{draft["village_name"]}乡村振兴规划报告（原始版）", "markdown")
            print(f"开始生成综合报告\n")
            
            # 调用 report_in_batches 方法生成报告
            final_report = await self.report_in_batches(draft, batch_size=3)
            
            # 更新 draft
            if "report" not in draft:
                draft["report"] = {}
            draft["report"] = final_report

            save_dict_to_file(draft, "Results", f"{draft["village_name"]}乡村振兴规划报告（整合版）", "markdown",keys=["report"])
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
        model="google/gemini-2.0-flash-thinking-exp:free",
        plan={
            "当前核心产业": "当前核心产业发展方案内容...",
            "未来核心产业": "未来核心产业发展方案内容...",
            # 其他任务的发展方案内容...
        }
    )

    # 初始化综合报告生成智能体，设置并发限制为3
    report_generator = Reportor_2()

    # 生成综合报告
    result_draft = asyncio.run(report_generator.generate_report(draft=draft))

    # 假设 save_dict_to_file 是一个保存字典到文件的函数
    # save_dict_to_file(result_draft, "Results\Output", f"{result_draft['village_name']}乡村振兴规划报告", "markdown", keys=["report"])