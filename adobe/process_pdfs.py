import os
import json
from pathlib import Path
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar
import fitz  
import pytesseract
from PIL import Image
import io
import re
from collections import Counter
from langdetect import detect, DetectorFactory
from concurrent.futures import ThreadPoolExecutor

DetectorFactory.seed = 0  

def is_heading_candidate(text):
    if len(text) > 80 or len(text) < 3:
        return False
    if "," in text and len(text.split(",")) > 2:
        return False  
    if text.count(" ") > 10:
        return False   
    if any(char.isdigit() for char in text) and len(text.split()) > 8:
        return False  
    if text.lower() in ["table of contents", "contents", "index"]:
        return False
    if text.isupper() and len(text) < 10:
        return False  
    if re.match(r"^page \\d+$", text.lower()):
        return False
    if text.endswith("..."):
        return False
    if text.count(":") > 1:
        return False
    if re.match(r"^[0-9]+$", text.strip()):
        return False
    if re.match(r"^[ivxlc]+$", text.strip().lower()):
        return False  
    return True

def extract_ocr_headings(pdf_path, existing_headings):
    doc = fitz.open(pdf_path)
    ocr_headings = []
    existing_texts = set(h['text'] for h in existing_headings)
    image_tasks = []
    page_indices = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        for img_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            base_image = doc.extract_image(xref)
            img_bytes = base_image["image"]
            image_tasks.append(img_bytes)
            page_indices.append(page_num)

    def ocr_image(image_bytes):
        try:
            image = Image.open(io.BytesIO(image_bytes))
            text = pytesseract.image_to_string(image, lang='eng+fra+spa+deu+hin+por+nld').strip()
            if text:
                try:
                    lang = detect(text)
                    lang_map = {
                        'en': 'eng',
                        'fr': 'fra',
                        'es': 'spa',
                        'de': 'deu',
                        'hi': 'hin',
                        'pt': 'por',
                        'nl': 'nld',
                    }
                    tesseract_lang = lang_map.get(lang, 'eng')
                    text = pytesseract.image_to_string(image, lang=tesseract_lang).strip()
                except Exception:
                    pass
            return text
        except Exception:
            return None

    with ThreadPoolExecutor() as executor:
        results = list(executor.map(ocr_image, image_tasks))

    for idx, text in enumerate(results):
        if text and text not in existing_texts:
            ocr_headings.append({
                'level': 'H3',
                'text': text,
                'page': page_indices[idx] + 1
            })
            existing_texts.add(text)
    return ocr_headings

def extract_headings_and_title(pdf_path):
    headings = []
    font_sizes = []
    text_elements = []
    title = None
    title_candidates = []
    boldnesses = []
    positions = []
    y_positions = []
    all_lines = []
    page_line_texts = []

    
    for page_num, page_layout in enumerate(extract_pages(pdf_path), start=1):
        page_lines = []
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                for text_line in element:
                    line_text = text_line.get_text().strip()
                    if not line_text:
                        continue
                    page_lines.append(line_text)
        page_line_texts.append(page_lines)
        all_lines.extend(page_lines)

   
    line_counts = Counter(all_lines)
    min_repeats = max(2, len(page_line_texts) // 3)
    repeated_lines = {line for line, count in line_counts.items() if count >= min_repeats}

    
    for page_num, page_layout in enumerate(extract_pages(pdf_path), start=1):
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                for text_line in element:
                    line_text = text_line.get_text().strip()
                    if not line_text or line_text in repeated_lines:
                        continue
                    
                    if hasattr(text_line, '__iter__'):
                        sizes = [char.size for char in text_line if isinstance(char, LTChar)]
                        bolds = [char.fontname for char in text_line if isinstance(char, LTChar)]
                    else:
                        sizes = []
                        bolds = []
                    if not sizes:
                        continue
                    avg_size = sum(sizes) / len(sizes) if sizes else 0
                    is_bold = any('Bold' in font for font in bolds)
                    x0 = text_line.x0
                    y0 = text_line.y0
                    font_sizes.append(avg_size)
                    boldnesses.append(int(is_bold))
                    positions.append(x0)
                    y_positions.append(y0)
                    text_elements.append({
                        'text': line_text,
                        'size': avg_size,
                        'bold': is_bold,
                        'x0': x0,
                        'y0': y0,
                        'page': page_num
                    })
                    if page_num == 1:
                        title_candidates.append({'text': line_text, 'size': avg_size})

    
    if not font_sizes:
        return None, []
    
    sorted_sizes = sorted(font_sizes)
    n = len(sorted_sizes)
    def percentile(data, perc):
        k = (len(data)-1) * (perc/100)
        f = int(k)
        c = min(f+1, len(data)-1)
        if f == c:
            return data[int(k)]
        d0 = data[f] * (c-k)
        d1 = data[c] * (k-f)
        return d0 + d1
    lower = percentile(sorted_sizes, 5)
    upper = percentile(sorted_sizes, 95)
    filtered_sizes = [s for s in font_sizes if lower <= s <= upper]
    if not filtered_sizes:
        filtered_sizes = font_sizes
    
    unique_sizes = sorted(set(filtered_sizes), reverse=True)
    n_clusters = min(3, len(unique_sizes))
    if n_clusters == 3:
        cluster_centers = [unique_sizes[0], unique_sizes[len(unique_sizes)//2], unique_sizes[-1]]
    elif n_clusters == 2:
        cluster_centers = [unique_sizes[0], unique_sizes[-1]]
    else:
        cluster_centers = [unique_sizes[0]]
    
    level_map = {}
    for i, c in enumerate(cluster_centers):
        if i == 0:
            level_map[c] = 'H1'
        elif i == 1:
            level_map[c] = 'H2'
        else:
            level_map[c] = 'H3'
    
    for elem in text_elements:
       
        closest = min(cluster_centers, key=lambda c: abs(elem['size'] - c))
        level = level_map[closest]
        
        if (level in ['H1', 'H2'] and (elem['bold'] or elem['x0'] < 100 or elem['x0'] > 200)) or (level == 'H3'):
            if is_heading_candidate(elem['text']) and elem['y0'] > 100:
                heading = {
                    'level': level,
                    'text': elem['text'],
                    'page': elem['page']
                }
                headings.append(heading)
    
    if title_candidates:
        title = max(title_candidates, key=lambda x: x['size'])['text']
    else:
        title = Path(pdf_path).stem
    return title, headings

def process_pdfs():
    
    input_dir = Path("/app/input")
    output_dir = Path("/app/output")

    
    output_dir.mkdir(parents=True, exist_ok=True)

    
    pdf_files = list(input_dir.glob("*.pdf"))

    for pdf_file in pdf_files:
        
        title, outline = extract_headings_and_title(str(pdf_file))
        
        ocr_headings = extract_ocr_headings(str(pdf_file), outline)
        outline.extend(ocr_headings)
        output_data = {
            "title": title,
            "outline": outline
        }
        
        output_file = output_dir / f"{pdf_file.stem}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        print(f"Processed {pdf_file.name} -> {output_file.name}")

if __name__ == "__main__":
    print("Starting processing pdfs")
    process_pdfs()
    print("completed processing pdfs")
