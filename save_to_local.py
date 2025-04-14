import os
import docx
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem

def format_nested_dict_to_text(nested_dict, indent=0):
    """将嵌套字典格式化为文本"""
    text = ""
    for key, value in nested_dict.items():
        text += " " * indent + f"**{key}**:\n"
        if isinstance(value, dict):
            text += format_nested_dict_to_text(value, indent + 4)
        else:
            text += " " * (indent + 4) + f"{value}\n"
    return text

def save_to_word(data, file_path):
    """将数据保存为Word文件"""
    doc = docx.Document()
    doc.add_heading('金田村乡村振兴规划报告', 0)
    
    for key, value in data.items():
        doc.add_heading(key, level=1)
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                doc.add_heading(sub_key, level=2)
                if isinstance(sub_value, dict):
                    for item_key, item_value in sub_value.items():
                        doc.add_paragraph(f"**{item_key}**: {item_value}")
                else:
                    doc.add_paragraph(sub_value)
        else:
            doc.add_paragraph(value)
    
    doc.save(file_path)
    print(f"Word文件已保存到: {file_path}")

def save_to_pdf(data, file_path):
    """将数据保存为PDF文件"""
    doc = SimpleDocTemplate(file_path, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    
    elements.append(Paragraph('金田村乡村振兴规划报告', styles['Title']))
    elements.append(Spacer(1, 12))
    
    for key, value in data.items():
        elements.append(Paragraph(key, styles['Heading2']))
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                elements.append(Paragraph(sub_key, styles['Heading3']))
                if isinstance(sub_value, dict):
                    for item_key, item_value in sub_value.items():
                        elements.append(Paragraph(f"**{item_key}**: {item_value}", styles['Normal']))
                else:
                    elements.append(Paragraph(sub_value, styles['Normal']))
        else:
            elements.append(Paragraph(value, styles['Normal']))
        elements.append(Spacer(1, 12))
    
    doc.build(elements)
    print(f"PDF文件已保存到: {file_path}")

def save_data_to_file(data, file_path):
    """将数据保存为Word或PDF文件"""
    # 检查文件路径是否存在，如果不存在则创建
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    
    if file_path.endswith('.docx'):
        save_to_word(data, file_path)
    elif file_path.endswith('.pdf'):
        save_to_pdf(data, file_path)
    else:
        raise ValueError("不支持的文件格式，仅支持 .docx 和 .pdf")


if __name__=="__main__":
    # 示例数据
    data = {
        'draft': [],
        'Village_name': '金田村',
        'Documents_path': 'Resource',
        'Document': {
            '梅州市金田村乡村政策调研报告': '# 梅州市泗水镇金田村乡村振兴政策研究报告\n\n本报告旨在深入调研并分析梅州市泗水镇金田村的乡村发展政策...',
            '梅州市金田村乡村现状调研报告': '# 金田村乡村振兴战略实施现状调研报告\n\n金田村，隶属于广东省梅州市平远县泗水镇，坐落于粤闽两省三县交界处...'
        },
        'Local_Condition': {
            'Natural': {
                '海拔高度': '村自然条件优劣势分析...',
                '湖泊分布': '### 金田村自然条件优劣势分析...'
            },
            'Policy': {
                '推进城乡融合发展，构建城乡统一的建设用地市场，推动人才、技术等要素向乡村流动': '### 一、金田村区位分析...',
                '细化村庄分类标准，科学确定发展目标': '### 一、金田村区位分析...'
            }
        }
    }

    # 调用函数保存数据
    file_path = "C:/path/to/your/file/report.docx"  # 替换为你的文件路径
    save_data_to_file(data, file_path)