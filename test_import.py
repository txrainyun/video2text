
import sys
import traceback

print("Testing imports...")
print("=" * 50)

try:
    print("1. Testing fastapi...")
    import fastapi
    print(f"   ✓ fastapi {fastapi.__version__} imported")
except Exception as e:
    print(f"   ✗ fastapi failed: {e}")

try:
    print("2. Testing uvicorn...")
    import uvicorn
    print(f"   ✓ uvicorn imported")
except Exception as e:
    print(f"   ✗ uvicorn failed: {e}")

try:
    print("3. Testing whisper...")
    import whisper
    print(f"   ✓ whisper imported")
except Exception as e:
    print(f"   ✗ whisper failed: {e}")
    print("   This is expected if you haven't installed it yet.")

try:
    print("4. Testing torch...")
    import torch
    print(f"   ✓ torch {torch.__version__} imported")
    print(f"   - CUDA available: {torch.cuda.is_available()}")
except Exception as e:
    print(f"   ✗ torch failed: {e}")

print("\n" + "=" * 50)
print("Test completed!")
