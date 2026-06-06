部署到 Render（快速指南）

1. 登录 Render：打开 https://render.com 并使用 GitHub 账户登录（或注册）。

2. 连接仓库：在 Render 控制台选择 New -> Web Service，选择通过 GitHub 关联的仓库 txrainyun/video2text。Render 会读取仓库根目录下的 render.yaml 并自动配置服务。

3. 服务类型：选择 Docker（仓库包含 Dockerfile），Plan 可选择 free（测试）或付费计划。

4. 环境变量：确认或添加环境变量：
   - PORT=8000（默认）

5. 初次部署注意事项：
   - 仓库不会包含本地 models/（已在 .dockerignore 中排除）。容器首次运行时，faster-whisper 可能会在启动或首次转录时下载模型，需耐心等待。
   - 若担心首次下载耗时或带宽，可在私有镜像中预装模型并在 Render 上使用私有镜像部署，或将模型放在可挂载的持久存储（Render 目前不直接支持大文件挂载）。

6. 部署后访问：Render 会提供一个域名（如 https://video2text.onrender.com），打开即可访问网页界面并上传文件。

7. 排错小贴士：
   - 如果上传返回失败，查看 Render 日志（Dashboard -> Services -> Logs），关注容器 stderr/stdout。
   - 确保 ffmpeg 可用（Dockerfile 已安装 ffmpeg）。
   - 模型下载失败可能是网络或 HF 镜像问题，检查网络或设置 HF_ENDPOINT 环境变量。

如需，我可以：
- 在 README.md 添加上述部署步骤（我可以自动提交）。
- 生成一个预构建镜像的 GitHub Actions 工作流并推送至 GitHub Container Registry（方便快速部署）。
