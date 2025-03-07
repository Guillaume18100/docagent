# Enterprise Document Automation Backend

A Django-based backend for enterprise document automation, featuring document processing, NLP analysis, and AI-powered document generation.

## Features

- **Document Ingestion**: Upload and process documents using OCR and text extraction
- **NLP Processing**: Analyze user input and generate clarifying questions using Hugging Face Transformers
- **Document Generation**: Generate draft documents using open-source generative AI models

## Technology Stack

- **Framework**: Django with Django REST Framework
- **Document Processing**: pytesseract (OCR) and tika-python (text extraction)
- **NLP Engine**: Hugging Face Transformers with optional LangChain integration
- **Document Generation**: Integration with open-source GPT models (GPT4All)

## Project Structure

```
/docautomation_backend/
├── manage.py
├── docautomation_backend/       # Project settings
├── document_processing/         # Document upload and processing
├── nlp/                         # NLP analysis module
├── document_generation/         # Document generation module
└── requirements.txt
```

## Setup Instructions

1. **Clone the repository**:

   ```
   git clone <repository-url>
   cd docautomation_backend
   ```

2. **Create and activate a virtual environment**:

   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:

   ```
   pip install -r requirements.txt
   ```

4. **Install Tesseract OCR**:
   - On macOS: `brew install tesseract`
   - On Ubuntu: `sudo apt-get install tesseract-ocr`
   - On Windows: Download and install from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)

5. **Install Apache Tika** (requires Java):
   - Ensure Java is installed on your system
   - The tika-python library will download the Tika server automatically

6. **Set up environment variables**:
   Create a `.env` file in the project root with:

   ```
   DEBUG=True
   SECRET_KEY=your-secret-key
   ```

7. **Run migrations**:

   ```
   python manage.py makemigrations
   python manage.py migrate
   ```

8. **Start the development server**:

   ```
   python manage.py runserver
   ```

## API Endpoints

### Document Processing

- `POST /api/documents/upload/`: Upload a document for processing
- `GET /api/documents/`: List all processed documents
- `GET /api/documents/{id}/`: Get details of a specific document

### NLP Processing

- `POST /api/nlp/analyze/`: Analyze user input and generate clarifying questions
- `POST /api/nlp/conversation/`: Continue a conversation with follow-up questions

### Document Generation

- `POST /api/generate/`: Generate a document based on processed data

## Testing

Run tests with:

```
pytest
```

## License

[MIT License](LICENSE)
