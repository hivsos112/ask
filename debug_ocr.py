from cnocr import CnOcr
from PIL import Image
import pandas as pd
from rapidfuzz import process, fuzz

import re

def filter_noise(text):
    # Filter out timestamps (e.g. 20:16:14, 2025-12-09)
    if re.search(r'\d{2}:\d{2}:\d{2}', text):
        return True
    # Filter out dates (e.g. 2025-12-09)
    if re.search(r'\d{4}-\d{2}-\d{2}', text):
        return True
    # Filter out short numeric strings or IDs
    # Match strings that are mostly alphanumeric/symbols and short
    # content with Chinese characters should NOT be matched here
    if re.match(r'^[a-zA-Z0-9/:-]+$', text) and len(text) < 15:
        return True
        
    # Heuristic: Filter lines with high digit density (e.g. "帆/01096" -> 5/7 digits)
    digit_count = sum(c.isdigit() for c in text)
    if len(text) > 0 and (digit_count / len(text)) > 0.6:
        return True
        
    return False

def test_ocr_and_search():
    # 1. Load Data
    try:
        df = pd.read_excel('题库.xlsx', header=1)
        df = df.fillna('')
        questions = df['题目'].astype(str).tolist()
    except Exception:
        questions = []

    ocr = CnOcr()

    def run_on_image(img_path):
        print(f"\n>>> Testing {img_path}")
        try:
            image = Image.open(img_path).convert('RGB')
            print(f"Original Size: {image.size}")
            
            # Automatic orientation detection
            def get_ocr_score(img):
                res = ocr.ocr(img)
                if not res:
                    return 0, []
                avg_score = sum(line['score'] for line in res) / len(res)
                return avg_score, res

            score_0, res_0 = get_ocr_score(image)
            image_180 = image.rotate(180)
            score_180, res_180 = get_ocr_score(image_180)
            
            final_res = res_0 if score_0 > score_180 else res_180
            orientation = '0 deg' if score_0 > score_180 else '180 deg'
            best_score = max(score_0, score_180)
            
            print(f"Selected Orientation: {orientation}, Avg Score: {best_score:.4f}")

            text_list = []
            for line in final_res:
                text = line['text']
                if not filter_noise(text):
                    text_list.append(text)
            
            extracted_text = ' '.join(text_list)
            print(f"Extracted Text: {extracted_text}")
            return extracted_text
        except Exception as e:
            print(f"Error: {e}")
            return ""

    run_on_image('test2.jpeg') # 4032x3024
    run_on_image('test3.jpeg') # 1280x1707


if __name__ == "__main__":
    test_ocr_and_search()
