# Document Automation System

A comprehensive document automation system that uses AI to extract text from documents, generate clarifying questions, and create new documents based on user requirements.

## Features

- **Document Upload & Processing**: Upload documents in various formats (PDF, DOCX, TXT, images)
- **Text Extraction**: Extract text from documents using OCR and Apache Tika
- **AI-Powered Document Generation**: Generate new documents based on user requirements
- **Multiple Output Formats**: Generate documents in DOCX, PDF, TXT, Markdown, or HTML formats
- **Reference Documents**: Use uploaded documents as references for generating new content

## AI Components

This system integrates several open-source AI models and libraries:

### 1. Document Ingestion & Text Extraction
- **Tesseract OCR**: Extracts text from images and scanned documents
- **Apache Tika**: Extracts text and metadata from various document formats

### 2. NLP Processing for Clarifying Questions
- **Hugging Face Transformers (GPT-2)**: Generates clarifying questions based on user inputs
- **Fallback System**: Rule-based question generation when AI models are unavailable

### 3. Document Generation
- **GPT4All**: Local AI model for generating document content
- **Format Conversion**: Converts AI-generated content to various document formats

## Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- Tesseract OCR (for image processing)
- Java Runtime Environment (for Apache Tika)

### Backend Setup
1. Create a virtual environment:
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   cd docautomation_backend
   pip install -r requirements.txt
   ```

3. Run migrations:
   ```
   python manage.py migrate
   ```

4. Start the backend server:
   ```
   python manage.py runserver
   ```

### Frontend Setup
1. Install dependencies:
   ```
   cd src
   npm install
   ```

2. Start the development server:
   ```
   npm run dev
   ```

## Usage

1. **Upload a Document**: Use the upload interface to submit a document
2. **Generate a New Document**: 
   - Select the "Generate Documents" tab
   - Enter a title and choose an output format
   - Write a detailed prompt describing the document you want
   - Click "Generate Document"
3. **Download the Generated Document**: Once processing is complete, download your document

## AI Model Configuration

The system is designed to work with or without AI models installed:

- **With AI Models**: Full functionality with AI-powered text extraction, question generation, and document creation
- **Without AI Models**: Fallback to basic text extraction and template-based generation

### Installing Optional AI Components

For full AI functionality, install these additional components:

1. **Tesseract OCR**:
   - Linux: `sudo apt-get install tesseract-ocr`
   - macOS: `brew install tesseract`
   - Windows: Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)

2. **GPT4All**:
   The system will automatically download the model file on first use.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
