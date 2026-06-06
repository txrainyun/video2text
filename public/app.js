class Video2TextApp {
    constructor() {
        this.tasks = new Map();
        this.currentTaskId = null;
        this.currentResult = null;
        this.pollingInterval = null;
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.loadTasks();
        this.checkModelStatus();
    }
    
    bindEvents() {
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        
        // 上传区域点击
        uploadArea.addEventListener('click', () => fileInput.click());
        
        // 文件选择
        fileInput.addEventListener('change', (e) => this.handleFiles(e.target.files));
        
        // 拖拽事件
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            this.handleFiles(e.dataTransfer.files);
        });
        
        // 模型切换
        document.getElementById('modelSelect').addEventListener('change', (e) => {
            this.switchModel(e.target.value);
        });
        
        // 结果操作按钮
        document.getElementById('copyBtn').addEventListener('click', () => this.copyText());
        document.getElementById('exportTxtBtn').addEventListener('click', () => this.exportFile('txt'));
        document.getElementById('exportMdBtn').addEventListener('click', () => this.exportFile('md'));
        document.getElementById('exportSrtBtn').addEventListener('click', () => this.exportFile('srt'));
    }
    
    async handleFiles(files) {
        for (const file of files) {
            await this.uploadFile(file);
        }
    }
    
    async uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error('上传失败');
            }
            
            const data = await response.json();
            this.tasks.set(data.file_id, {
                filename: data.filename,
                status: 'queued'
            });
            this.renderTasks();
            this.startPolling(data.file_id);
            
        } catch (error) {
            console.error('上传错误:', error);
            this.showToast('上传失败: ' + error.message, 'error');
        }
    }
    
    startPolling(taskId) {
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
        }
        
        this.pollingInterval = setInterval(async () => {
            await this.checkStatus(taskId);
        }, 1000);
    }
    
    async checkStatus(taskId) {
        try {
            const response = await fetch(`/status/${taskId}`);
            const data = await response.json();
            
            this.tasks.set(taskId, {
                ...this.tasks.get(taskId),
                status: data.status,
                progress: data.progress,
                error: data.error
            });
            
            this.renderTasks();
            
            if (data.status === 'completed' || data.status === 'failed') {
                if (data.status === 'completed') {
                    await this.loadResult(taskId);
                }
                this.stopPollingIfAllDone();
            }
            
        } catch (error) {
            console.error('状态检查错误:', error);
        }
    }
    
    stopPollingIfAllDone() {
        const allDone = Array.from(this.tasks.values()).every(
            task => task.status === 'completed' || task.status === 'failed'
        );
        
        if (allDone && this.pollingInterval) {
            clearInterval(this.pollingInterval);
            this.pollingInterval = null;
        }
    }
    
    async loadResult(taskId) {
        try {
            const response = await fetch(`/result/${taskId}`);
            const result = await response.json();
            
            this.currentTaskId = taskId;
            this.currentResult = result;
            
            this.renderResult(result);
            this.showResultSection();
            
        } catch (error) {
            console.error('加载结果错误:', error);
        }
    }
    
    renderTasks() {
        const tasksList = document.getElementById('tasksList');
        
        if (this.tasks.size === 0) {
            tasksList.innerHTML = '<div class="empty-state"><p>暂无转录任务</p></div>';
            return;
        }
        
        tasksList.innerHTML = Array.from(this.tasks.entries()).map(([id, task]) => `
            <div class="task-item ${task.status}">
                <div class="task-info">
                    <div class="task-filename">${task.filename}</div>
                    <div class="task-status">${this.getStatusText(task)}</div>
                    ${task.status === 'processing' ? `
                        <div class="task-progress">
                            <div class="task-progress-bar" style="width: ${task.progress}%"></div>
                        </div>
                    ` : ''}
                </div>
                <div class="task-actions">
                    ${task.status === 'completed' ? `
                        <button class="btn btn-small" onclick="app.viewResult('${id}')">查看</button>
                    ` : ''}
                    ${task.status !== 'processing' ? `
                        <button class="btn btn-small" onclick="app.deleteTask('${id}')">删除</button>
                    ` : ''}
                </div>
            </div>
        `).join('');
    }
    
    getStatusText(task) {
        const statusMap = {
            'queued': '等待中...',
            'processing': `转录中 ${task.progress}%`,
            'completed': '已完成 ✓',
            'failed': `失败: ${task.error || '未知错误'}`
        };
        return statusMap[task.status] || task.status;
    }
    
    renderResult(result) {
        const resultContent = document.getElementById('resultContent');
        const resultMeta = document.getElementById('resultMeta');
        
        resultMeta.innerHTML = `
            <div class="result-meta-item">
                <span class="result-meta-label">语言</span>
                <span class="result-meta-value">${result.language}</span>
            </div>
            <div class="result-meta-item">
                <span class="result-meta-label">时长</span>
                <span class="result-meta-value">${this.formatDuration(result.duration)}</span>
            </div>
        `;
        
        resultContent.innerHTML = result.segments.map(seg => `
            <div class="result-segment">
                <div class="segment-time">${this.formatTimestamp(seg.start)} - ${this.formatTimestamp(seg.end)}</div>
                <div class="segment-text">${seg.text}</div>
            </div>
        `).join('');
    }
    
    showResultSection() {
        document.getElementById('resultSection').style.display = 'block';
    }
    
    viewResult(taskId) {
        if (this.tasks.has(taskId)) {
            const task = this.tasks.get(taskId);
            if (task.status === 'completed') {
                this.loadResult(taskId);
                window.scrollTo({
                    top: document.getElementById('resultSection').offsetTop,
                    behavior: 'smooth'
                });
            }
        }
    }
    
    async deleteTask(taskId) {
        try {
            await fetch(`/task/${taskId}`, { method: 'DELETE' });
            this.tasks.delete(taskId);
            this.renderTasks();
            
            if (this.currentTaskId === taskId) {
                this.currentTaskId = null;
                this.currentResult = null;
                document.getElementById('resultSection').style.display = 'none';
            }
            
        } catch (error) {
            console.error('删除任务错误:', error);
        }
    }
    
    async loadTasks() {
        try {
            const response = await fetch('/tasks');
            const tasks = await response.json();
            
            tasks.forEach(task => {
                this.tasks.set(task.id, {
                    filename: task.filename,
                    status: task.status,
                    progress: task.progress
                });
            });
            
            this.renderTasks();
            
            // 如果有进行中的任务，开始轮询
            const hasActive = tasks.some(t => 
                t.status === 'queued' || t.status === 'processing'
            );
            if (hasActive) {
                tasks.forEach(t => {
                    if (t.status !== 'completed' && t.status !== 'failed') {
                        this.startPolling(t.id);
                    }
                });
            }
            
        } catch (error) {
            console.error('加载任务列表错误:', error);
        }
    }
    
    async checkModelStatus() {
        const statusIndicator = document.querySelector('.status-indicator');
        const statusText = document.querySelector('.status-text');
        
        try {
            const response = await fetch('/health');
            const data = await response.json();
            
            if (data.model_loaded) {
                statusIndicator.classList.add('ready');
                statusText.textContent = '模型已就绪';
            } else {
                statusText.textContent = '模型加载中...';
                setTimeout(() => this.checkModelStatus(), 2000);
            }
            
        } catch (error) {
            statusText.textContent = '服务连接中...';
            setTimeout(() => this.checkModelStatus(), 2000);
        }
    }
    
    async switchModel(modelName) {
        try {
            const response = await fetch(`/model?model_name=${modelName}`, {
                method: 'POST'
            });
            
            if (response.ok) {
                this.showToast('模型切换成功', 'success');
            } else {
                throw new Error('切换失败');
            }
            
        } catch (error) {
            this.showToast('模型切换失败', 'error');
        }
    }
    
    copyText() {
        if (!this.currentResult) return;
        
        const text = this.currentResult.text;
        navigator.clipboard.writeText(text).then(() => {
            this.showToast('已复制到剪贴板', 'success');
        }).catch(() => {
            this.showToast('复制失败', 'error');
        });
    }
    
    async exportFile(format) {
        if (!this.currentTaskId || !this.currentResult) return;
        
        try {
            const includeTimestamps = format !== 'srt';
            const response = await fetch(
                `/export/${this.currentTaskId}?format=${format}&include_timestamps=${includeTimestamps}`
            );
            
            const data = await response.json();
            const blob = new Blob([data.content], { type: 'text/plain;charset=utf-8' });
            const url = URL.createObjectURL(blob);
            
            const a = document.createElement('a');
            a.href = url;
            a.download = data.filename;
            a.click();
            
            URL.revokeObjectURL(url);
            this.showToast(`已导出 ${data.filename}`, 'success');
            
        } catch (error) {
            console.error('导出错误:', error);
            this.showToast('导出失败', 'error');
        }
    }
    
    formatTimestamp(seconds) {
        const h = Math.floor(seconds / 3600);
        const m = Math.floor((seconds % 3600) / 60);
        const s = Math.floor(seconds % 60);
        const ms = Math.floor((seconds % 1) * 1000);
        return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')},${ms.toString().padStart(3, '0')}`;
    }
    
    formatDuration(seconds) {
        const m = Math.floor(seconds / 60);
        const s = Math.floor(seconds % 60);
        return `${m}分${s}秒`;
    }
    
    showToast(message, type = 'info') {
        const existing = document.querySelector('.toast');
        if (existing) existing.remove();
        
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        document.body.appendChild(toast);
        
        setTimeout(() => toast.remove(), 3000);
    }
}

const app = new Video2TextApp();
