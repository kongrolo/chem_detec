import logging
from config import settings
from pipelines import TextProcessingPipeline
# 初始化日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
def main():
    print("Initializing pipeline...")
    try:
        # 初始化处理流水线
        pipeline = TextProcessingPipeline(
            yolo_config=settings.YOLO_CONFIG,
            ocr_config=settings.OCR_CONFIG,
            lm_config=settings.LM_CONFIG,
            instructions=settings.INSTRUCTION_TEMPLATES
        )
        print("Pipeline initialized successfully")
        
        # 处理示例图片
        test_image = "test_bottle.jpg"
        print(f"Processing test image: {test_image}")
        results = pipeline.process(test_image)
        if not results:
            print("未检测到任何化学试剂瓶")
        for idx, result in enumerate(results, 1):
            print(f"\n结果 {idx}:")
            print(f"类别: {result['class']}")
            print(f"置信度: {result['confidence']:.2f}")
            print(f"瓶体位置: {result['bottle_bbox']}")
            print(f"标签位置: {result['label_bbox']}")
            print(f"识别文本: {result['text']}")
            print(f"使用指令: {result['instruction']}")
            print(f"模型分析:\n{result['analysis']}")
            print(f"安全信息: {result['safety_info']}")
    except Exception as e:
        logging.error(f"处理失败: {str(e)}", exc_info=True)
if __name__ == "__main__":
    main()
