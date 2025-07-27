## 🧠 Adobe Challenge 1A – PDF Heading Extraction

Welcome to our solution for **Challenge 1A: Outline Generation from PDFs** in the **Adobe India Hackathon**!

Our approach is designed to work seamlessly on both **digitally generated** and **scanned (image-based)** PDFs. It is **language-aware**, **OCR-enabled**, and meets all of Adobe’s system and output requirements.

---

## 🚀 1) Our Approach

We designed a hybrid, multi-phase pipeline to robustly extract:

* 📌 The **document title**
* 📚 A hierarchical **outline of section headings (H1/H2/H3)**

### ✅ Step-by-step Strategy:

1. **📄 PDF Parsing with Font Analysis**

   * We use `pdfminer.six` to analyze every text element.
   * Extract font size, boldness, and position to infer structure.
   * Repeated headers/footers are filtered using frequency-based heuristics.

2. **🧠 Heuristic Heading Classification**

   * Font sizes are clustered into **H1**, **H2**, **H3** using a 3-bin method.
   * Additional heuristics ensure the text is **short**, **relevant**, and **not noisy**.

3. **🏷️ Title Extraction**

   * On the first page, we select the **largest font size line** as the document title.
   * If not found, fall back to the file name.

4. **🖼️ OCR for Scanned PDFs**

   * Uses `PyMuPDF` to extract embedded images.
   * Applies `Tesseract OCR` (with 7+ languages) via `pytesseract`.
   * OCR-detected text is filtered and added as **H3 headings** if not duplicates.

5. **📦 Structured Output**

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

## 🧰 2) Libraries & Technologies Used

| Category                   | Tools & Libraries Used                                                                                                |
| -------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| 👨‍💻 Programming Language | Python 3.10                                                                                                           |
| 📄 PDF Parsing             | [`pdfminer.six`](https://pypi.org/project/pdfminer.six/), [`PyMuPDF`](https://pymupdf.readthedocs.io/en/latest/)      |
| 🔍 OCR                     | [`pytesseract`](https://pypi.org/project/pytesseract/), [`Tesseract OCR`](https://github.com/tesseract-ocr/tesseract) |
| 🖼️ Image Processing       | [`Pillow`](https://pillow.readthedocs.io/en/stable/)                                                                  |
| 🌐 Language Detection      | [`langdetect`](https://pypi.org/project/langdetect/)                                                                  |
| ⚙️ Multithreading          | `concurrent.futures.ThreadPoolExecutor`                                                                               |
| 📁 Path Handling           | `pathlib`, `os`, `json`, `collections`                                                                                |

> ✅ OCR support includes: English, Hindi, French, Spanish, German, Portuguese, Dutch

---

## 🛠️ 3) Build & Run Instructions

### 🐳 Docker Instructions

#### ✅ Folder Structure

```
📦 adobe/
├── Dockerfile
├── process_pdfs.py
├── requirements.txt
```

---

#### 📥 Step 1: Build the Docker Image

```bash
docker build -t adobe-outline-extractor .
```

---

#### 📂 Step 2: Place PDFs in `input/` folder

```bash
mkdir input output
# Add your PDFs into the input/ folder
```

---

#### ▶️ Step 3: Run the Container

```bash
docker run \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  adobe-outline-extractor
```

---

#### 📤 Step 4: View the Output

Each PDF will generate a `.json` file in the `/output` directory with its extracted outline.

---

## ✅ Why This Works Well

* 🧠 Smart heuristics + OCR fallback = robust across document types
* ⚡ Fast and multithreaded OCR for speed
* 📜 Purely CPU-based – meets all Adobe constraints
* 🧩 Language-aware – detects + adapts to multilingual content

---

Let me know if you’d like this dropped into a file or need a submission-ready ZIP 📦.
