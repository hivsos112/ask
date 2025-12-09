import traceback
import sys
import os

def main():
    try:
        print('Checking imports...', flush=True)
        
        # cv2 package name is opencv-python-headless
        print('Importing cv2...', flush=True)
        try:
            import cv2
            print(f'cv2 imported successfully: {cv2.__version__}', flush=True)
        except ImportError:
            print("ImportError: cv2 not found. Trying to find installed packages...", flush=True)
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "list"])
            raise

        print('Importing onnxruntime...', flush=True)
        import onnxruntime
        print(f'onnxruntime imported successfully: {onnxruntime.__version__}', flush=True)
        
        print('Importing cnocr...', flush=True)
        from cnocr import CnOcr
        print('cnocr imported successfully', flush=True)
        
        print('Downloading CnOCR model...', flush=True)
        ocr = CnOcr()
        print('Model downloaded and initialized successfully.', flush=True)
        
    except Exception:
        print("An error occurred during model download/verification:", flush=True)
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
