FROM --platform=linux/amd64 python:3.10-slim

WORKDIR /app

# System dependencies for OCR, fonts, and PDF handling
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-fra \
    tesseract-ocr-deu \
    tesseract-ocr-spa \
    tesseract-ocr-hin \
    tesseract-ocr-por \
    tesseract-ocr-nld \
    libgl1 \
    libglib2.0-0 \
    poppler-utils \
    fonts-dejavu \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your script
COPY process_pdfs.py .

# Run the script (the system will call this)
CMD ["python", "process_pdfs.py"]

