import requests
import json
import logging

logger = logging.getLogger(__name__)

class LMClient:
    def __init__(self, config):
        self.config = config
        
    def generate_prompt(self, instruction):
        return [{
            "role": "user",
            "content": instruction
        }]
    
    def query(self, prompt):
        try:
            response = requests.post(
                self.config["api_url"],
                json={
                    "messages": prompt,
                    "temperature": self.config["temperature"],
                    "max_tokens": self.config["max_tokens"]
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except requests.exceptions.RequestException as e:
            logger.error(f"API请求失败: {str(e)}")
            return "模型请求失败"
        except json.JSONDecodeError:
            logger.error("响应解析失败")
            return "响应解析失败"
