import whisper
from pathlib import Path
import torch

class WhisperModel:
    def __init__(self, model_name: str = "base", device: str = "auto"):
        self.model_name = model_name
        self.device = self._get_device(device)
        self.model = None
        
    def _get_device(self, device: str) -> str:
        if device == "auto":
            if torch.cuda.is_available():
                return "cuda"
            return "cpu"
        return device
    
    def load_model(self):
        self.model = whisper.load_model(self.model_name, device=self.device)
        return self.model
    
    def get_model_info(self):
        return {
            "name": self.model_name,
            "device": self.device,
            "available": ["tiny", "base", "small", "medium", "large"]
        }

model_manager = WhisperModel()
