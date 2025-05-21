# 化学品标签识别系统 API 服务

这是一个用于识别化学品标签并提供安全信息的API服务。该服务可以与微信小程序集成，提供化学品信息查询功能。

## 功能特点

- 图片上传和处理
- OCR文字识别
- 化学品信息查询
- 信息格式化展示
- RESTful API接口
- 支持跨域请求
- 自动文件管理
- 详细的错误处理和日志记录

## 文件结构

```
project/
├── input/          # 上传的图片存储目录
├── output/         # OCR处理结果存储目录
├── core/           # 核心处理模块
├── api_server.py   # API服务器
└── requirements.txt # 项目依赖
```

## 安装要求

- Python 3.8+
- FastAPI
- Uvicorn
- OpenCV
- 其他依赖见 requirements.txt

## 安装步骤

1. 克隆仓库：
```bash
git clone [repository-url]
cd [repository-name]
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 启动服务器：
```bash
python api_server.py
```

服务器将在 http://localhost:8000 启动

## API 接口

API接口在 project/config/setting.py 中进行更改。

### 1. 健康检查
- 端点：`GET /`
- 描述：检查API服务是否正常运行

### 2. 处理图片
- 端点：`POST /api/process/image`
- 参数：file (图片文件)
- 描述：上传图片并进行处理，返回识别结果和化学品信息

### 3. 列出文件
- 端点：`GET /api/files/list`
- 描述：列出input和output文件夹中的文件

### 4. 清理文件
- 端点：`DELETE /api/files/cleanup`
- 描述：清理超过24小时的文件


