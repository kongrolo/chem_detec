from pathlib import Path
import os

# 基础目录验证
try:
    BASE_DIR = Path(__file__).parent.parent.resolve(strict=True)  # 严格模式验证路径存在性
except FileNotFoundError:
    raise RuntimeError("配置文件目录结构异常，请检查项目完整性")

# 模型路径配置（使用原始字符串+Path组合）
MODEL_ROOT = Path(r"D:\yolo\package\models")  # 此处修改为你的实际模型存储路径

YOLO_CONFIG = {
    # 绝对路径配置方式（推荐方案）
    "model_path": MODEL_ROOT / "best.pt",  # Path对象自动处理路径分隔符
    
    # 备选方案：直接使用原始字符串
    # "model_path": r"D:\AI_Models\YOLO-LM-System\detection\yolov8n.pt",
    
    "confidence_threshold": 0.3,  # Lower threshold for test image
    "device": "cpu"
}

OCR_CONFIG = {
    # PP-OCR模型绝对路径配置
    "rec_model_dir": str(MODEL_ROOT / "ocr" / "ch_PP-OCRv4_rec"),
    "det_model_dir": str(MODEL_ROOT / "ocr" / "ch_PP-OCRv4_det"),
    "cls_model_dir": str(MODEL_ROOT / "ocr" / "ch_ppocr_mobile_v2.0_cls"),
    "lang": "ch"
}

LM_CONFIG = {
    # SiliconFlow API配置
    "api_base": "https://api.siliconflow.com/v1",  # SiliconFlow API基础地址
    "api_endpoint": "/chat/completions",     # 标准OpenAI兼容端点
    "model": "gpt-4",  # 使用的模型名称
    
    # 连接参数
    "timeout": 30.0,        # 超时时间
    "temperature": 0.7,
    "max_tokens": 512,
    
    # API密钥配置
    "api_key": "sk-xpsqvsemifkjgmyhmirdjrgmlienuruptkzpeefhuktffmqt",  # 需要替换为实际的API密钥
    
    # 流式传输配置
    "stream": False
}

# 指令模板
INSTRUCTION_TEMPLATES = {
    "default": "请分析以下文本内容: {}",
    "chemical": "请分析以下化学品标签信息，提供化学名称、分子式、危险性、安全操作指南和储存要求: {}",
    "hazardous": "请分析以下危险化学品标签，详细说明其危险性分类、防护措施、应急处理和处置方法: {}",
    "liquid": "请分析以下液体化学品标签，提供其物理化学性质、相容性、泄漏处理和急救措施: {}"
}

# 路径有效性验证
_required_paths = [
    YOLO_CONFIG["model_path"],
    Path(OCR_CONFIG["rec_model_dir"]),
    Path(OCR_CONFIG["det_model_dir"]),
]

for path in _required_paths:
    if not path.exists():
        raise FileNotFoundError(f"关键模型文件缺失：{path}")
