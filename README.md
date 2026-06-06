# Video2Text - 本地音视频转文字工具

一键将音视频文件转写为文字，支持字幕导出。

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动服务
python app.py

# 3. 打开浏览器访问
#    http://127.0.0.1:8000
```

Windows 用户可直接双击 `start.bat`（英文）或 `启动.bat`（中文）一键启动。

## 功能

- 上传视频/音频文件（MP4、MP3、WMV、AVI、MOV、MKV 等常见格式）
- 使用 Whisper 模型自动转写文字
- 查看完整转写结果和分段内容
- 导出 TXT / Markdown / SRT 字幕格式
- 多队列处理

## 项目文件结构

```
video2text/
├── app.py              # 主服务（FastAPI）
├── whisper_model.py    # Whisper 模型管理
├── transcription.py    # 转写服务
├── requirements.txt    # Python 依赖
├── public/             # 前端页面
│   ├── index.html
│   ├── style.css
│   └── app.js
├── tests/              # 测试
│   ├── test_api.py
│   ├── test_transcription.py
│   └── test_whisper_model.py
├── start.bat           # 一键启动（英文）
├── 启动.bat            # 一键启动（中文）
├── uploads/            # 上传文件目录（自动创建）
├── models/             # 模型缓存目录（自动创建）
└── .gitignore
```

## 系统要求

- Python 3.8+
- 内存：推荐 8GB+
- 磁盘：Whisper base 模型约 140MB，large 约 3GB
- ffmpeg（可选，处理视频文件时需要）

## 配置

默认使用 Whisper base 模型（140MB，速度和精度均衡）。
可在网页界面中切换到 tiny / small / medium / large 模型。

## 许可证

MIT
