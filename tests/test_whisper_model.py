import pytest
from whisper_model import WhisperModel

def test_model_initialization():
    model = WhisperModel("base", "cpu")
    assert model.model_name == "base"
    assert model.device == "cpu"
    assert model.model is None

def test_get_model_info():
    model_manager = WhisperModel()
    info = model_manager.get_model_info()
    assert "name" in info
    assert "device" in info
    assert "available" in info
    assert len(info["available"]) > 0