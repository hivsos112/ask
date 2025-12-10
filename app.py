from flask import Flask, request, jsonify, render_template, send_from_directory
import pandas as pd
from rapidfuzz import process, fuzz
import os
import re
from cnocr import CnOcr
from PIL import Image

app = Flask(__name__)

# Global variables
df = None
ocr_model = None
questions_spaced = []

def preprocess_text(text):
    """
    Insert spaces between characters for Chinese tokenization support in RapidFuzz.
    """
    return ' '.join(list(str(text).replace(' ', '')))

def filter_noise(text):
    """
    Filter out OCR noise like timestamps, dates, and short alphanumeric codes.
    """
    # Filter out timestamps (e.g. 20:16:14)
    if re.search(r'\d{2}:\d{2}:\d{2}', text):
        return True
    # Filter out dates (e.g. 2025-12-09)
    if re.search(r'\d{4}-\d{2}-\d{2}', text):
        return True
    # Filter out short numeric strings or IDs (e.g. 096210, 一帆/01)
    # Match strings that are mostly alphanumeric/symbols and short
    # content with Chinese characters should NOT be matched here
    if re.match(r'^[a-zA-Z0-9/:-]+$', text) and len(text) < 15:
        return True
        
    # Heuristic: Filter lines with high digit density (e.g. "帆/01096" -> 5/7 digits)
    # This filters out watermarks like "Name/ID"
    digit_count = sum(c.isdigit() for c in text)
    if len(text) > 0 and (digit_count / len(text)) > 0.6:
        return True
        
    return False

def load_data():
    global df, ocr_model, questions_spaced
    try:
        # Load the excel file, assuming header is on the second row (index 1)
        df = pd.read_excel('题库.xlsx', header=1)
        # Fill NaN with empty string
        df = df.fillna('')
        
        # Pre-process questions for search
        print("Preprocessing questions...")
        questions = df['题目'].astype(str).tolist()
        questions_spaced = [preprocess_text(q) for q in questions]
        
        print("Data loaded successfully.")
    except Exception as e:
        print(f"Error loading data: {e}")
        df = pd.DataFrame() # Empty dataframe fallback
        questions_spaced = []

    try:
        print("Loading OCR model...")
        # det_model_name='en_PP-OCRv3_det', rec_model_name='en_PP-OCRv3_rec' could be used for english, 
        # but default is good for chinese/english mix.
        ocr_model = CnOcr() 
        print("OCR model loaded.")
    except Exception as e:
        print(f"Error loading OCR model: {e}")

def perform_search(query):
    if not query:
        return []
    if df is None or df.empty:
        return []

    # Preprocess query for token_set_ratio
    query_spaced = preprocess_text(query)
    
    # Use token_set_ratio with spaced characters for better Chinese matching + noise handling
    # We use questions_spaced which is pre-calculated
    matches = process.extract(query_spaced, questions_spaced, limit=20, scorer=fuzz.token_set_ratio)
    
    results = []
    for match_spaced, score, index in matches:
        if score > 40: 
            row = df.iloc[index]
            result = {
                'question': row['题目'],
                'answer': row['答案'],
                'options': {
                    'A': row['A'],
                    'B': row['B'],
                    'C': row['C'],
                    'D': row['D'],
                    'E': row['E'],
                    'F': row['F']
                },
                'remark': row['备注']
            }
            results.append(result)
            
    return results

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/<path:filename>.txt')
def serve_txt(filename):
    return send_from_directory(app.root_path, f'{filename}.txt')

@app.route('/api/search')
def search():
    query = request.args.get('q', '')
    results = perform_search(query)
    return jsonify(results)

def get_ocr_score(img):
    res = ocr_model.ocr(img)
    if not res:
        return 0, []
    avg_score = sum(line['score'] for line in res) / len(res)
    return avg_score, res

@app.route('/api/ocr', methods=['POST'])
def ocr_search():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    try:
        image = Image.open(file.stream).convert('RGB')
        
        if ocr_model is None:
             return jsonify({'error': 'OCR model not loaded'}), 500

        # Resize image if too large (standardize input)
        max_dimension = 1600
        if max(image.size) > max_dimension:
            scale = max_dimension / max(image.size)
            new_size = (int(image.size[0] * scale), int(image.size[1] * scale))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
            print(f"Image resized to: {image.size}")

        # Automatic orientation detection (0 vs 180 degrees)
        # Calculate score for 0 degree
        score_0, res_0 = get_ocr_score(image)
        print(f"OCR Score (0 deg): {score_0}")
        
        # Calculate score for 180 degree
        image_180 = image.rotate(180)
        score_180, res_180 = get_ocr_score(image_180)
        print(f"OCR Score (180 deg): {score_180}")
        
        # Select best orientation
        final_res = res_0 if score_0 > score_180 else res_180
        print(f"Selected Orientation: {'0 deg' if score_0 > score_180 else '180 deg'}")

        # Filter noise and join with spaces
        text_list = []
        for line in final_res:
            text = line['text']
            if not filter_noise(text):
                text_list.append(text)
                
        extracted_text = ' '.join(text_list)
        print(f"Extracted text: {extracted_text}")
        
        if not extracted_text:
             return jsonify({'text': '', 'results': []})

        results = perform_search(extracted_text)
        return jsonify({'text': extracted_text, 'results': results})
        
    except Exception as e:
        print(f"OCR Error: {e}")
        return jsonify({'error': str(e)}), 500

# Load data at module level so Gunicorn/Production server initializes it
load_data()

if __name__ == '__main__':
    # When running directly (dev mode), load_data is called here.
    # But we also call it at module level below for production (Gunicorn).
    # To avoid double loading in dev, we can check if it's already loaded, 
    # but load_data is idempotent-ish (just overwrites globals).
    # Ideally, just call it at module level.
    app.run(host='0.0.0.0', port=5001, debug=True)
