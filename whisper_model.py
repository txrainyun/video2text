from faster_whisper import WhisperModel as FWWhisperModel
from pathlib import Path
import os

# 本地模型路径映射（已预下载的模型）
LOCAL_MODEL_MAP = {
    "base": str(Path(__file__).parent / "models" / "faster-whisper-base"),
}

# HuggingFace 镜像（用于下载尚未预下载的模型）
HF_MIRROR = "https://hf-mirror.com"

class WhisperModel:
    MODEL_SIZES = {
        "tiny": "39M",
        "base": "140M",
        "small": "466M",
        "medium": "1.5G",
        "large": "2.9G",
        "large-v2": "2.9G",
        "large-v3": "2.9G",
        "turbo": "1.6G",
    }

    def __init__(self, model_name: str = "base", device: str = "auto"):
        self.model_name = model_name
        self.device = self._get_device(device)
        self.model = None
        self.model_dir = Path("models")
        self.model_dir.mkdir(exist_ok=True)
        self.compute_type = "float32"

    def _get_device(self, device: str) -> str:
        if device == "auto":
            return "cpu"
        return device

    def _get_model_path(self):
        """获取模型路径：优先使用本地已下载的模型"""
        if self.model_name in LOCAL_MODEL_MAP:
            local_path = LOCAL_MODEL_MAP[self.model_name]
            if Path(local_path).exists():
                return local_path
        return self.model_name

    def load_model(self, verbose: bool = True):
        if self.model is None:
            model_path = self._get_model_path()
            if verbose:
                print(f"正在加载 Whisper 模型: {self.model_name} ({self.MODEL_SIZES.get(self.model_name, 'unknown')})...")
                print(f"模型路径: {model_path}")
                print(f"设备: {self.device}, 计算精度: {self.compute_type}")

            # 设置镜像环境变量
            os.environ["HF_ENDPOINT"] = HF_MIRROR

            self.model = FWWhisperModel(
                model_path,
                device=self.device,
                compute_type=self.compute_type,
                download_root=str(self.model_dir),
            )
            if verbose:
                print("模型加载完成！")
        return self.model

    def get_model_info(self):
        return {
            "name": self.model_name,
            "device": self.device,
            "size": self.MODEL_SIZES.get(self.model_name, "unknown"),
            "available": list(self.MODEL_SIZES.keys()),
        }

    def switch_model(self, new_model: str):
        if new_model not in self.MODEL_SIZES:
            raise ValueError(f"Model {new_model} not available")
        self.model_name = new_model
        self.model = None
        return self.load_model()
