<div align="left">
  <img src="https://github.com/akhilthirunalveli/akhilthirunalveli/blob/main/assets/1%20(2).png" alt="App Demo" width="1000"/>
  <img src="https://github.com/akhilthirunalveli/akhilthirunalveli/blob/main/assets/2%20(2).png" alt="App Demo" width="1000"/>
</div>

## Our Approach

- Our approach is designed to work seamlessly on both **digitally generated** and **scanned (image-based)** PDFs.
- It is **language-aware**, **OCR-enabled**, and meets all of Adobe’s system and output requirements.
- We ingest the PDF as a stream of data, analyzing each text block for features like font size, weight, and position. 
- Our algorithms then cluster these features to differentiate the Title, H1, H2, and H3 headings from standard text. 
- We use this classification to reconstruct the document's logical flow into a hierarchical tree structure. The final output is this clean, structured outline you see. 
---



We designed a hybrid, multi-phase pipeline to robustly extract:

* The **document title**
* A hierarchical **outline of section headings (H1/H2/H3)**

### Step-by-step Strategy:

1. **PDF Parsing with Font Analysis**

   * We use `pdfminer.six` to analyze every text element.
   * Extract font size, boldness, and position to infer structure.
   * Repeated headers/footers are filtered using frequency-based heuristics.

2. **Heuristic Heading Classification**

   * Font sizes are clustered into **H1**, **H2**, **H3** using a 3-bin method.
   * Additional heuristics ensure the text is **short**, **relevant**, and **not noisy**.

3. **Title Extraction**

   * On the first page, we select the **largest font size line** as the document title.
   * If not found, fall back to the file name.

4. **OCR for Scanned PDFs**

   * Uses `PyMuPDF` to extract embedded images.
   * Applies `Tesseract OCR` (with 7+ languages) via `pytesseract`.
   * OCR-detected text is filtered and added as **H3 headings** if not duplicates.

5. **Structured Output**

   * Produces a JSON like:

     ```json
     {
       "title": "Document Title",
       "outline": [
         { "level": "H1", "text": "Introduction", "page": 1 },
         ...
       ]
     }
     ```

---

## Libraries & Technologies Used

| Category                   | Tools & Libraries Used                                                                                                |
| -------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| 👨‍💻 Programming Language | Python 3.10                                                                                                           |
| 📄 PDF Parsing             | [`pdfminer.six`](https://pypi.org/project/pdfminer.six/), [`PyMuPDF`](https://pymupdf.readthedocs.io/en/latest/)      |
| 🔍 OCR                     | [`pytesseract`](https://pypi.org/project/pytesseract/), [`Tesseract OCR`](https://github.com/tesseract-ocr/tesseract) |
| 🖼️ Image Processing       | [`Pillow`](https://pillow.readthedocs.io/en/stable/)                                                                  |
| 🌐 Language Detection      | [`langdetect`](https://pypi.org/project/langdetect/)                                                                  |
| ⚙️ Multithreading          | `concurrent.futures.ThreadPoolExecutor`                                                                               |
| 📁 Path Handling           | `pathlib`, `os`, `json`, `collections`                                                                                |

> OCR support includes: English, Hindi, French, Spanish, German, Portuguese, Dutch

---

## Build & Run Instructions

### Docker Instructions

#### Folder Structure

```
📦 adobe/
├── Dockerfile
├── process_pdfs.py
├── requirements.txt
```

---

#### Step 1: Build the Docker Image

```bash
docker build -t adobe-outline-extractor .
```

---

#### Step 2: Place PDFs in `input/` folder

```bash
mkdir input output
# Add your PDFs into the input/ folder
```

---

#### Step 3: Run the Container

```bash
docker run \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  adobe-outline-extractor
```

---

#### Step 4: View the Output

Each PDF will generate a `.json` file in the `/output` directory with its extracted outline.

---

## Why This Works Well

We implemented a robust PDF outline generation system by combining structural analysis with optical character recognition (OCR) to handle both digitally-generated and scanned documents. Using pdfminer.six, we parsed each page to extract text elements along with their font sizes, boldness, and positions, allowing us to infer hierarchical headings (H1, H2, H3) through clustering and heuristics. Repeated elements like headers and footers were intelligently filtered out based on their frequency across pages. To support image-based PDFs, we integrated Tesseract OCR via pytesseract, applying multilingual recognition (including Hindi, French, Spanish, and more) and threading for performance. Detected headings from OCR were seamlessly merged with the digital text structure to produce a comprehensive and language-aware outline, all wrapped in a Dockerized solution adhering to Adobe’s constraints.

* 📜 Purely CPU-based – meets all Adobe constraints
* 🧩 Language-aware – detects + adapts to multilingual content

