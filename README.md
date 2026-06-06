# Video2Text - 本地音视频转文字工具

一款本地运行的网页应用，将视频/音频文件批量转录为文字稿，支持可选导出时间轴字幕。

## 功能特性

- ✅ 批量上传视频/音频文件
- ✅ 队列式转录处理
- ✅ 完整文字稿展示
- ✅ 多种导出格式（TXT/Markdown/SRT）
- ✅ Whisper 模型管理
- ✅ 响应式前端界面

## 系统要求

- Python 3.8+
- ffmpeg（用于视频转音频）
- 内存：建议 8GB+
- 磁盘：预留 3GB+ 用于 Whisper 模型
- GPU（可选）：如有 NVIDIA GPU，转录速度会大幅提升

## 安装步骤

### 1. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 2. 安装 ffmpeg（Windows）

从 https://ffmpeg.org/download.html 下载并添加到 PATH

### 3. 启动应用

```bash
python app.py
```

### 4. 访问应用

打开浏览器访问：http://127.0.0.1:8000

## 使用说明

1. **上传文件**：拖拽或点击选择视频/音频文件
2. **选择模型**：根据需求选择 Whisper 模型大小
3. **等待转录**：查看转录进度
4. **查看结果**：点击"查看"按钮查看转录内容
5. **导出文件**：选择导出格式（TXT/Markdown/SRT）

## Whisper 模型说明

| 模型 | 大小 | 速度 | 准确度 |
|------|------|------|--------|
| tiny | 39MB | 最快 | 较低 |
| base | 140MB | 快 | 中等 |
| small | 466MB | 较快 | 较高 |
| medium | 1.5GB | 较慢 | 高 |
| large | 2.9GB | 慢 | 最高 |

## 项目结构

```
video2text/
├── app.py                 # FastAPI 主应用
├── transcription.py        # 转录核心逻辑
├── whisper_model.py       # Whisper 模型管理
├── requirements.txt       # Python 依赖
├── public/               # 前端静态文件
│   ├── index.html       # 主页面
│   ├── style.css        # 样式文件
│   └── app.js          # 前端逻辑
├── uploads/             # 临时上传目录
└── models/              # Whisper 模型缓存
```

## 注意事项

- 首次使用会自动下载 Whisper 模型
- 建议使用 base 或 small 模型，平衡速度和准确度
- 转录过程在本地完成，数据完全私密
- 可以随时切换不同的 Whisper 模型

## 技术栈

- 后端：Python / FastAPI
- 语音识别：OpenAI Whisper
- 前端：HTML / CSS / JavaScript

## License

MIT
