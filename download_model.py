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
        # Manually download the model files using huggingface_hub
        from huggingface_hub import hf_hub_download
        import zipfile
        import shutil

        CNOCR_MODELS_REPO = "breezedeus/cnstd-cnocr-models"
        
        # 1. Download and extract Rec model (densenet_lite_136-gru)
        # We use the ONNX version as onnxruntime is installed and preferred
        rec_model_name = "densenet_lite_136-gru"
        rec_zip_path = "models/cnocr/2.3/densenet_lite_136-gru-onnx.zip"
        
        # Target directory: ~/.cnocr/2.3/densenet_lite_136-gru
        cnocr_root = os.path.join(os.path.expanduser("~"), ".cnocr", "2.3", rec_model_name)
        if not os.path.exists(cnocr_root):
            os.makedirs(cnocr_root, exist_ok=True)
            
        print(f"Downloading {rec_zip_path}...", flush=True)
        try:
            downloaded_file = hf_hub_download(repo_id=CNOCR_MODELS_REPO, filename=rec_zip_path)
            print(f"Extracting to {cnocr_root}...", flush=True)
            with zipfile.ZipFile(downloaded_file, 'r') as zip_ref:
                zip_ref.extractall(cnocr_root)
        except Exception as e:
            print(f"Failed to download/extract {rec_model_name}: {e}", flush=True)
            # Fallback or continue to let CnOcr try

        # 2. Download and extract Det model (ch_PP-OCRv3_det)
        # We explicitly choose v3 because v5 seems missing in the repo but requested by default
        det_model_name = "ch_PP-OCRv3_det"
        det_zip_path = "models/cnstd/1.2/ch_PP-OCRv3_det_infer-onnx.zip"
        
        # Target directory: ~/.cnstd/1.2/ppocr/ch_PP-OCRv3_det
        # Note: CnStd might expect a specific structure. 
        # Usually it's ~/.cnstd/1.2/ppocr/{model_name}
        cnstd_root = os.path.join(os.path.expanduser("~"), ".cnstd", "1.2", "ppocr", det_model_name)
        if not os.path.exists(cnstd_root):
            os.makedirs(cnstd_root, exist_ok=True)
            
        print(f"Downloading {det_zip_path}...", flush=True)
        try:
            downloaded_file = hf_hub_download(repo_id=CNOCR_MODELS_REPO, filename=det_zip_path)
            print(f"Extracting to {cnstd_root}...", flush=True)
            with zipfile.ZipFile(downloaded_file, 'r') as zip_ref:
                zip_ref.extractall(cnstd_root)
        except Exception as e:
            print(f"Failed to download/extract {det_model_name}: {e}", flush=True)

        # Initialize CnOcr with the specific models we downloaded
        print(f"Initializing CnOcr with rec_model_name={rec_model_name}, det_model_name={det_model_name}...", flush=True)
        ocr = CnOcr(rec_model_name=rec_model_name, det_model_name=det_model_name)
        print('Model downloaded and initialized successfully.', flush=True)
        
    except Exception:
        print("An error occurred during model download/verification:", flush=True)
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
