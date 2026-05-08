# Record Extraction System (RES)
### A program designed to retrieve medical record data from hospital databases for research purposes, specifically to automate data entry. This system utilizes advanced OCR techniques and Large Language Models (LLMs) to transform raw image data into structured JSON formats.

## 🚀 Overview

RES automates the labor-intensive process of manual data entry from scanned medical records. By combining **PaddleOCR** for text extraction and **Qwen2.5 7B** for intelligent data parsing, the system can handle complex medical tables, varying document layouts, and historical record nuances.

## 🛠 Tech Stack

* **Processor:** Intel i7-6700
* **GPU:** AMD Radeon RX 580 (8GB VRAM)
* **Memory:** 20GB RAM
* **OCR Engine:** [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)
* **Inference Engine:** [llama-cpp-python](https://github.com/abetlen/llama-cpp-python)
* **Language Model:** Qwen2.5 7B
* **Environment:** Local Server (Privacy-focused, no cloud usage)

## 🏗 Pipeline Architecture

1.  **Image Processing:** Normalization and enhancement using PIL/OpenCV.
2.  **OCR Execution:** PaddleOCR extracts raw text strings with spatial awareness.
3.  **Master Cleaning:** A regex-based pipeline strips administrative "noise" and redundant tables.
4.  **Visit Grouping:** Individual pages are correlated and combined by visit date.
5.  **LLM Extraction:** The structured text is processed by Qwen2.5 to extract high-value clinical data points.
