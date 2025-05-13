from ultralytics import YOLO
import logging

logger = logging.getLogger(__name__)

class YOLODetector:
    def __init__(self, config):
        self.config = config
        self.model = self._load_model()
        
    def _load_model(self):
        try:
            model = YOLO(self.config["model_path"])
            model.fuse()
            return model
        except Exception as e:
            logger.error(f"模型加载失败: {str(e)}")
            raise
        
    def detect(self, image_path):
        print(f"Loading image from: {image_path}")
        results = self.model(image_path)[0]
        print(f"Detection completed, found {len(results.boxes)} potential objects")
        detections = []
        for box in results.boxes:
            conf = box.conf.item()
            print(f"Object detected with confidence: {conf:.2f}")
            if conf > self.config["confidence_threshold"]:
                bbox = box.data.tolist()[0]
                # Assume label is in top 30% of bottle
                x1, y1, x2, y2 = bbox[:4]
                label_bbox = [
                    x1,
                    y1,
                    x2,
                    min(y1 + (y2-y1)*0.3, y2)  # Label region height
                ]
                detections.append({
                    "bottle": bbox,
                    "label": label_bbox,
                    "confidence": box.conf.item(),
                    "class_id": int(box.cls.item())
                })
        return detections
