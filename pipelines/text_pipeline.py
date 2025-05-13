import cv2
from PIL import Image
from typing import List, Dict
from core import YOLODetector, OCRProcessor, InstructionManager, LMClient

class TextProcessingPipeline:
    def __init__(self, yolo_config, ocr_config, lm_config, instructions):
        self.detector = YOLODetector(yolo_config)
        self.ocr = OCRProcessor(ocr_config)
        self.instruction_mgr = InstructionManager(instructions)
        self.lm_client = LMClient(lm_config)
        self.class_names = self.detector.model.names

    def _crop_image(self, image_path, detections):
        image = cv2.imread(image_path)
        bottle_crops = []
        label_crops = []
        for det in detections:
            # Crop bottle region
            x1, y1, x2, y2 = map(int, det['bottle'][:4])
            bottle_crop = image[y1:y2, x1:x2]
            bottle_crops.append(Image.fromarray(cv2.cvtColor(bottle_crop, cv2.COLOR_BGR2RGB)))
            
            # Crop label region
            x1, y1, x2, y2 = map(int, det['label'][:4])
            label_crop = image[y1:y2, x1:x2]
            label_crops.append(Image.fromarray(cv2.cvtColor(label_crop, cv2.COLOR_BGR2RGB)))
            
        return bottle_crops, label_crops

    def process(self, image_path) -> List[Dict]:
        # 目标检测
        detections = self.detector.detect(image_path)
        
        # 裁剪区域
        bottle_images, label_images = self._crop_image(image_path, detections)
        
        # OCR处理 (only on label regions)
        ocr_results = [self.ocr.process_image(img) for img in label_images]
        
        # 构造结果
        output = []
        for det, text in zip(detections, ocr_results):
            class_name = self.class_names[det['class_id']]
            
            # 生成化学专用指令
            instruction = self.instruction_mgr.get_instruction(
                "chemical" if "chemical" in class_name.lower() else class_name,
                text
            )
            
            # 模型查询
            prompt = self.lm_client.generate_prompt(instruction)
            analysis = self.lm_client.query(prompt)
            
            output.append({
                "class": class_name,
                "confidence": det['confidence'],
                "bottle_bbox": list(map(int, det['bottle'][:4])),
                "label_bbox": list(map(int, det['label'][:4])),
                "text": text,
                "instruction": instruction,
                "analysis": analysis,
                "safety_info": "Chemical safety info will be added here"
            })
        
        return output
