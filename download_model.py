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
        # Manually download the model files using huggingface_hub if CLI is not working well or for robustness
        # This mirrors what cnocr might do but ensures it happens via python
        from huggingface_hub import hf_hub_download
        
        # Default models for CnOCR (as per v2.3+)
        # rec_model_name='densenet_lite_136-gru', det_model_name='ch_PP-OCRv3_det' (or similar)
        # The user log mentions: /root/.cnocr/2.3/densenet_lite_136-gru and /root/.cnstd/1.2/ppocr/ch_PP-OCRv5_det
        
        # It seems cnocr uses 'breezedeus/cnstd-cnocr-models' repo.
        # We will try to download them to the default location to satisfy cnocr.
        
        CNOCR_HOME = os.path.join(os.path.expanduser("~"), ".cnocr")
        CNSTD_HOME = os.path.join(os.path.expanduser("~"), ".cnstd")
        
        # Pre-download densenet_lite_136-gru
        # Based on search results, it seems these are in 'breezedeus/cnstd-cnocr-models'
        # The file might be a zip or individual files. 
        # Search results showed 'models/cnocr/2.1/densenet_lite_136-gru.zip'
        
        # However, to avoid guessing paths, we will rely on CnOcr's internal logic 
        # but ensure huggingface-cli is available (done above)
        # AND we will try to use python API to download if possible.
        
        # If the CLI fix works, the following line should succeed.
        ocr = CnOcr()
        print('Model downloaded and initialized successfully.', flush=True)
        
    except Exception:
        print("An error occurred during model download/verification:", flush=True)
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
