import requests
import json
from typing import Generator

class LMStudioClient:
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.base_url = self.config["api_base"]
        
        # 设置持久连接参数
        self.session.headers.update({
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config['api_key']}"
        })

    def _handle_response(self, response):
        """统一处理API响应"""
        if response.status_code == 401:
            raise ConnectionError("请启动LM Studio并启用服务器模式")
        if response.status_code != 200:
            raise RuntimeError(f"API错误 [{response.status_code}]: {response.text}")
        return response.json()

    def generate(self, prompt: str) -> str:
        """标准文本生成接口"""
        full_url = f"{self.base_url}{self.config['api_endpoint']}"
        
        payload = {
            "model": self.config["model"],
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.config["temperature"],
            "max_tokens": self.config["max_tokens"],
            "stream": self.config["stream"]
        }

        try:
            response = self.session.post(
                full_url,
                json=payload,
                timeout=self.config["timeout"]
            )
            result = self._handle_response(response)
            return result['choices'][0]['message']['content']
        except requests.exceptions.ConnectionError:
            raise RuntimeError("无法连接到LM Studio服务，请确认：\n"
                               "1. 已启动LM Studio\n"
                               "2. 已加载语言模型\n"
                               "3. 已启用'Server'模式 (左下角开关)")

    def stream_generate(self, prompt: str) -> Generator[str, None, None]:
        """流式文本生成接口"""
        payload = {
            "model": self.config["model"],
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.config["temperature"],
            "stream": True
        }

        with self.session.post(
            f"{self.base_url}{self.config['api_endpoint']}",
            json=payload,
            stream=True,
            timeout=self.config["timeout"]
        ) as response:
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line.decode('utf-8'))
                    if 'choices' in chunk:
                        yield chunk['choices'][0]['delta'].get('content', '')
