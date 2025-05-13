from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from core.chemical_info import ChemicalInfoRetriever
from core.ocr_processing import OCRProcessor
import cv2
import numpy as np
import io
import os
import logging
import time
from typing import Dict, Optional
import uvicorn
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="Chemical Label Recognition API")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化处理器
chemical_info = ChemicalInfoRetriever()
ocr_processor = OCRProcessor()

# 确保input和output文件夹存在
os.makedirs("input", exist_ok=True)
os.makedirs("output", exist_ok=True)

@app.get("/")
async def root():
    """健康检查接口"""
    return {"status": "ok", "message": "Chemical Label Recognition API is running"}

@app.post("/api/process/image")
async def process_image(
    file: UploadFile = File(...),
    isRealtime: str = Form('0')  # 0: 单张模式, 1: 实时模式
) -> Dict:
    """处理上传的图片并返回化学品信息"""
    try:
        is_realtime = isRealtime == '1'
        
        # 检查文件类型
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Only image files are allowed")
        
        # 实时模式下不保存文件
        if not is_realtime:
            # 生成唯一的文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            input_filename = f"input_{timestamp}.jpg"
            output_filename = f"output_{timestamp}.txt"
            
            # 保存上传的图片
            input_path = os.path.join("input", input_filename)
            output_path = os.path.join("output", output_filename)
            logger.info(f"Processing file: {file.filename}")
        
        try:
            # 读取上传的图片内容
            contents = await file.read()
            
            if not is_realtime:
                with open(input_path, "wb") as f:
                    f.write(contents)
            
            # 将二进制内容转换为OpenCV格式
            nparr = np.frombuffer(contents, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                raise HTTPException(status_code=400, detail="Invalid image file")
            
            # OCR处理
            logger.info("Starting OCR processing")
            text = ocr_processor.process_image(image)
            logger.info(f"OCR result: {text}")
            
            if not is_realtime:
                # 保存OCR结果
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(text)
            
            # 获取化学品信息
            logger.info("Getting chemical information")
            info = chemical_info.get_chemical_info(text)
            
            if not info:
                return JSONResponse(
                    status_code=200,
                    content={
                        "status": "success",
                        "data": {
                            "ocr_text": text,
                            "chemical_info": {},
                            "formatted_info": "未识别到化学品信息",
                            "input_file": input_filename if not is_realtime else None,
                            "output_file": output_filename if not is_realtime else None
                        }
                    }
                )
            
            # 格式化信息
            formatted_info = chemical_info.format_info(info)
            
            return {
                "status": "success",
                "data": {
                    "ocr_text": text,
                    "chemical_info": info,
                    "formatted_info": formatted_info,
                    "input_file": input_filename if not is_realtime else None,
                    "output_file": output_filename if not is_realtime else None
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing file: {str(e)}")
            if not is_realtime and 'input_path' in locals():
                if os.path.exists(input_path):
                    os.remove(input_path)
                if os.path.exists(output_path):
                    os.remove(output_path)
            raise HTTPException(status_code=500, detail=str(e))
            
    except Exception as e:
        logger.error(f"Error in process_image: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/files/list")
async def list_files() -> Dict:
    """列出input和output文件夹中的文件"""
    try:
        input_files = os.listdir("input")
        output_files = os.listdir("output")
        return {
            "status": "success",
            "data": {
                "input_files": input_files,
                "output_files": output_files
            }
        }
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/files/cleanup")
async def cleanup_files() -> Dict:
    """清理超过24小时的文件"""
    try:
        current_time = time.time()
        deleted_files = []
        
        # 清理input文件夹
        for filename in os.listdir("input"):
            filepath = os.path.join("input", filename)
            if os.path.getmtime(filepath) < current_time - 86400:  # 24小时
                os.remove(filepath)
                deleted_files.append(filepath)
        
        # 清理output文件夹
        for filename in os.listdir("output"):
            filepath = os.path.join("output", filename)
            if os.path.getmtime(filepath) < current_time - 86400:  # 24小时
                os.remove(filepath)
                deleted_files.append(filepath)
                
        return {
            "status": "success",
            "data": {
                "deleted_files": deleted_files
            }
        }
    except Exception as e:
        logger.error(f"Error cleaning up files: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=True) 