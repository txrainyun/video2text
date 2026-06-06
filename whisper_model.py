import whisper
from pathlib import Path
import torch
import hashlib
import os

class WhisperModel:
    MODEL_SIZES = {
        "tiny": "39M",
        "base": "140M",
        "small": "466M",
        "medium": "1.5G",
        "large": "2.9G"
    }
    
    def __init__(self, model_name: str = "base", device: str = "auto"):
        self.model_name = model_name
        self.device = self._get_device(device)
        self.model = None
        self.model_dir = Path("models")
        self.model_dir.mkdir(exist_ok=True)
        
    def _get_device(self, device: str) -> str:
        if device == "auto":
            if torch.cuda.is_available():
                return "cuda"
            return "cpu"
        return device
    
    def load_model(self, verbose: bool = True):
        if self.model is None:
            self.model = whisper.load_model(
                self.model_name,
                device=self.device,
                download_root=str(self.model_dir)
            )
        return self.model
    
    def get_model_info(self):
        return {
            "name": self.model_name,
            "device": self.device,
            "size": self.MODEL_SIZES.get(self.model_name, "unknown"),
            "available": list(self.MODEL_SIZES.keys())
        }
    
    def switch_model(self, new_model: str):
        if new_model not in self.MODEL_SIZES:
            raise ValueError(f"Model {new_model} not available")
        self.model_name = new_model
        self.model = None
        return self.load_model()

model_manager = WhisperModel()