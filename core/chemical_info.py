import requests
import logging
import json
import time
from typing import Dict, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from config.settings import LM_CONFIG  # 导入API配置

logger = logging.getLogger(__name__)

class ChemicalInfoRetriever:
    def __init__(self):
        self.api_url = LM_CONFIG["api_base"]
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {LM_CONFIG['api_key']}"
        }
        
        # 配置重试策略
        retry_strategy = Retry(
            total=3,  # 最大重试次数
            backoff_factor=1,  # 重试间隔
            status_forcelist=[429, 500, 502, 503, 504]  # 需要重试的HTTP状态码
        )
        
        # 创建会话并应用重试策略
        self.session = requests.Session()
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def get_chemical_info(self, chemical_name: str) -> Optional[Dict]:
        """获取化学品的详细信息"""
        try:
            prompt = f"""请提供以下化学品的详细安全信息。直接返回JSON格式数据，不要包含其他内容：
{{
    "chemical_name": {{
        "zh": "中文名",
        "en": "英文名"
    }},
    "formula": "分子式",
    "cas": "CAS号",
    "hazard_class": "危险性类别",
    "main_hazards": [
        "主要危害1",
        "主要危害2"
    ],
    "safety_measures": [
        "防护措施1",
        "防护措施2"
    ],
    "first_aid": [
        "急救措施1",
        "急救措施2"
    ],
    "storage": [
        "储存注意事项1",
        "储存注意事项2"
    ]
}}

化学品：{chemical_name}"""

            payload = {
                "messages": [
                    {"role": "system", "content": "你是一个化学品安全专家。请直接返回JSON格式的数据，不要包含任何其他内容。确保JSON格式正确。"},
                    {"role": "user", "content": prompt}
                ],
                "model": LM_CONFIG["model"],
                "temperature": LM_CONFIG["temperature"],
                "max_tokens": LM_CONFIG["max_tokens"],
                "stream": LM_CONFIG["stream"]
            }

            logger.info(f"发送请求到 {self.api_url}")
            
            # 使用配置的超时时间
            response = self.session.post(
                f"{self.api_url}{LM_CONFIG['api_endpoint']}",
                headers=self.headers,
                json=payload,
                timeout=(10, LM_CONFIG["timeout"])  # (连接超时, 读取超时)
            )
            
            logger.info(f"API响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    content = result['choices'][0]['message']['content']
                    
                    # 尝试从内容中提取JSON
                    try:
                        # 查找第一个有效的JSON对象
                        content = content.strip()
                        logger.debug(f"原始响应内容:\n{content}")
                        
                        # 如果内容以```json开头，去掉这个标记
                        if '```json' in content:
                            content = content[content.find('```json') + 7:]
                            if '```' in content:
                                content = content[:content.find('```')]
                        
                        content = content.strip()
                        logger.debug(f"清理后的内容:\n{content}")
                        
                        # 尝试修复不完整的JSON
                        if content.startswith('{') and not content.endswith('}'):
                            content = content + '}'
                        
                        try:
                            # 直接尝试解析整个内容
                            chemical_info = json.loads(content)
                            return chemical_info
                        except json.JSONDecodeError as e:
                            logger.warning(f"直接解析失败: {str(e)}")
                            # 尝试提取和修复第一个完整的JSON对象
                            start = content.find('{')
                            if start >= 0:
                                # 计算嵌套层级来找到正确的结束位置
                                level = 0
                                end = -1
                                for i in range(start, len(content)):
                                    if content[i] == '{':
                                        level += 1
                                    elif content[i] == '}':
                                        level -= 1
                                        if level == 0:
                                            end = i + 1
                                            break
                                
                                if end > start:
                                    json_str = content[start:end]
                                    try:
                                        chemical_info = json.loads(json_str)
                                        return chemical_info
                                    except json.JSONDecodeError:
                                        logger.error(f"解析提取的JSON失败: {json_str}")
                                        return None
                            
                            logger.error("未找到有效的JSON内容")
                            return None
                    except json.JSONDecodeError as e:
                        logger.error(f"JSON解析失败: {str(e)}")
                        logger.error(f"尝试解析的内容: {json_str}")
                        return None
                except KeyError as e:
                    logger.error(f"响应格式错误: {str(e)}")
                    logger.error(f"响应内容: {result}")
                    return None
            else:
                logger.error(f"API请求失败: {response.status_code}")
                logger.error(f"错误响应: {response.text}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"请求异常: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"未知错误: {str(e)}")
            logger.error(f"错误详情: {str(e.__class__.__name__)}: {str(e)}")
            return None

    def format_info(self, info: Dict) -> str:
        """格式化化学品信息为易读的文本格式"""
        if not info:
            return "无法获取化学品信息"

        try:
            # 构建每个部分的列表项
            main_hazards = "\n".join([f"- {h}" for h in info.get('main_hazards', [])])
            safety_measures = "\n".join([f"- {m}" for m in info.get('safety_measures', [])])
            first_aid = "\n".join([f"- {f}" for f in info.get('first_aid', [])])
            storage = "\n".join([f"- {s}" for s in info.get('storage', [])])

            text = f"""化学品安全信息卡
========================

【基本信息】
化学名称：{info.get('chemical_name', {}).get('zh', '未知')} / {info.get('chemical_name', {}).get('en', '未知')}
分子式：{info.get('formula', '未知')}
CAS号：{info.get('cas', '未知')}

【危险性】
危险性类别：{info.get('hazard_class', '未知')}

主要危害：
{main_hazards or '未提供主要危害信息'}

【安全防护】
防护措施：
{safety_measures or '未提供防护措施信息'}

【应急处置】
急救措施：
{first_aid or '未提供急救措施信息'}

【储存要求】
储存注意事项：
{storage or '未提供储存注意事项信息'}
"""
            return text
        except Exception as e:
            logger.error(f"格式化信息失败: {str(e)}")
            return "信息格式化失败" 