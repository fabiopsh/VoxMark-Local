import os
import requests

class ModelManager:
    def __init__(self, model_dir="models"):
        self.model_dir = model_dir
        if not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir)

import shutil
import wave
import struct
import math

import shutil
import os
import io
import wave
import struct
import math
import requests
# Try import, harmless if fails (we catch later or it fails at runtime)
try:
    from styletts2 import tts
except ImportError:
    tts = None

class ModelManager:
    def __init__(self, model_dir="models"):
        self.model_dir = model_dir
        if not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir)
        self.model = None
        
        # Check espeak immediately to setup PATH
        self.is_espeak_present()
        
        # Auto-load model if files exist
        if self.is_model_present():
            print("Model files found on startup, attempting to load...")
            try:
                # Reuse download_model logic which handles loading + checking files
                self.download_model() 
            except Exception as e:
                print(f"Startup load warning: {e}")

    def is_model_present(self):
        # Check for specific files
        return (os.path.exists(os.path.join(self.model_dir, "config.yml")) and 
                os.path.exists(os.path.join(self.model_dir, "epochs_2nd_00020.pth")))

    def is_espeak_present(self):
        # 1. Check standard PATH
        if shutil.which("espeak-ng") is not None or shutil.which("espeak") is not None:
             return True
        
        # 2. Check standard Windows Install Path
        possible_path = r"C:\Program Files\eSpeak NG"
        if os.path.exists(os.path.join(possible_path, "espeak-ng.exe")):
            print(f"Found eSpeak at {possible_path}, adding to PATH...")
            os.environ["PATH"] += os.pathsep + possible_path
            return True
            
        return False
        
    def is_ready(self):
        # Check espeak again to ensure PATH is updated if needed
        return self.model is not None and self.is_espeak_present()

    def download_model(self):
        # Hugging Face URL for StyleTTS2-LibriTTS
        base_url = "https://huggingface.co/yl4579/StyleTTS2-LibriTTS/resolve/main"
        # Correct filename based on repo check: epochs_2nd_00020.pth
        files = {
            "config.yml": f"{base_url}/Models/LibriTTS/config.yml",
            "epochs_2nd_00020.pth": f"{base_url}/Models/LibriTTS/epochs_2nd_00020.pth"
        }

        print("Starting model download...")
        for filename, url in files.items():
            path = os.path.join(self.model_dir, filename)
            if not os.path.exists(path):
                print(f"Downloading {filename}...")
                response = requests.get(url, stream=True)
                if response.status_code == 200:
                    with open(path, 'wb') as f:
                        shutil.copyfileobj(response.raw, f)
                    print(f"Downloaded {filename}")
                else:
                    print(f"Failed to download {filename}: {response.status_code}")
                    return False
        
        print("Download complete. Loading model...")
        
        if tts is None:
            print("WARNING: StyleTTS2 library not found (likely Python version issue). Skipping model load.")
            return True # Download was successful, just can't load.

        try:
            # We assume tts is imported or available. 
            # If installation failed, this might raise.
            self.model = tts.StyleTTS2(model_checkpoint_path=os.path.join(self.model_dir, "epochs_2nd_00020.pth"), 
                                     config_path=os.path.join(self.model_dir, "config.yml"))
            print("Model loaded.")
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False

    def synthesize(self, text):
        if not self.is_model_present():
            return None
        
        # If library is missing, use dummy immediately
        if tts is None:
             print("StyleTTS2 lib missing, using dummy synthesis.")
             return self._synthesize_dummy(text)
            
        if self.model is None:
            # Try to load if files exist
            try:
                self.model = tts.StyleTTS2(model_checkpoint_path=os.path.join(self.model_dir, "epochs_2nd_00020.pth"), 
                                         config_path=os.path.join(self.model_dir, "config.yml"))
            except Exception as e:
                print(f"Could not load model: {e}")
                # Fallback to dummy for POC if real one fails (e.g. library missing)
                return self._synthesize_dummy(text)
        
        try:
            # Code to run inference
            # We need to handle the output properly.
            # Assuming library usage:
            out = self.model.inference(text)
             
            # Convert to WAV bytes
            # If out is just audio array
            import numpy as np
            import scipy.io.wavfile as wav
            
            buffer = io.BytesIO()
            if hasattr(out, 'dtype') and out.dtype == np.float32:
                 out = (out * 32767).astype(np.int16)
            
            # Simple array check
            wav.write(buffer, 24000, out)
            return buffer.getvalue()
        except:
             return self._synthesize_dummy(text)

    def _synthesize_dummy(self, text):
        # Fallback for POC testing without heavy model
        sample_rate = 24000
        duration = 2.0 
        frequency = 440.0
        
        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            
            num_samples = int(sample_rate * duration)
            for i in range(num_samples):
                value = int(32767.0 * math.sin(2.0 * math.pi * frequency * i / sample_rate))
                data = struct.pack('<h', value)
                wav_file.writeframes(data)
                
        return buffer.getvalue()

model_manager = ModelManager()
