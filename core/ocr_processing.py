from paddleocr import PaddleOCR
import numpy as np
import logging
logger = logging.getLogger(__name__)
class OCRProcessor:
    def __init__(self, config):
        self.ocr = PaddleOCR(
            use_angle_cls=True,
            lang=config["lang"],
            use_gpu=config["use_gpu"],
            show_log=False
        )
    
    def process_image(self, image):
        try:
            result = self.ocr.ocr(np.array(image), cls=True)
            if result and result[0]:
                return " ".join([line[1][0] for line in result[0]])
            return ""
        except Exception as e:
            logger.error(f"OCR处理失败: {str(e)}")
            return ""