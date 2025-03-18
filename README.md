# DocAgent

DocAgent is a document automation platform that combines document processing, NLP analysis, and document generation capabilities. It provides a user-friendly interface for processing, analyzing, and generating documents with AI assistance.

## Features

- **Document Processing**: Extract text and structure from various document formats
- **NLP Analysis**: Perform named entity recognition, sentiment analysis, and more
- **Document Generation**: Create new documents based on templates and AI-generated content
- **RESTful API**: Integrate with your existing applications
- **Modern Web Interface**: User-friendly React-based UI

## Tech Stack

### Backend
- Django 4.2+
- Django REST Framework
- Tesseract OCR
- NLTK
- Transformers
- PyTorch

### Frontend
- React
- TypeScript
- Vite
- Tailwind CSS
- shadcn/ui

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn
- Optional: Docker and docker-compose for container-based deployment

### Installation & Running (Simplified)

```bash
# Clone the repository
git clone https://github.com/yourusername/docagent.git
cd docagent

# Set up the project (installs all dependencies)
make setup

# Start the application (automatically uses the best available method)
make start
```

The system will automatically:
1. Install all required dependencies (including NLP libraries)
2. Set up the database and apply migrations
3. Start both backend and frontend servers
4. Open the application in your browser

The application will be available at:
- Frontend: http://localhost:8080
- Backend API: http://localhost:8000/api
- Admin interface: http://localhost:8000/admin

### Alternative Methods

If you prefer to use a specific deployment method, you can still use:

```bash
# Start in local development mode
make start-dev

# Start using Docker
make start-docker
```

## AI Analysis Feature

DocAgent now includes automatic AI analysis for all uploaded documents. When you upload a document, the system will:

1. Extract text from the document
2. Generate a summary
3. Extract keywords and entities
4. Analyze sentiment and topics
5. Display the results in the "AI Analysis" tab

This feature is available in all deployment modes and requires no additional configuration.

## Troubleshooting

If you encounter any issues:

1. **Restart the application**:
   ```bash
   make start
   ```

2. **Rebuild from scratch** (Docker mode):
   ```bash
   make docker-rebuild
   ```

3. **Check logs**:
   ```bash
   # For Docker deployment
   docker-compose logs backend
   docker-compose logs frontend
   
   # For local development
   Check terminal output from the running servers
   ```

## Project Structure

```
docagent/
├── docautomation_backend/   # Django backend
│   ├── document_processing/ # Document processing app
│   ├── nlp/                 # NLP processing app
│   ├── document_generation/ # Document generation app
│   └── docautomation_backend/ # Main Django project settings
├── src/                     # React frontend
│   ├── components/          # React components
│   ├── context/             # React context providers
│   ├── pages/               # Page components
│   ├── services/            # API services
│   └── types/               # TypeScript type definitions
├── scripts/                 # Utility scripts
└── docker-compose.yml       # Docker Compose configuration
```

## API Documentation

The API documentation is available at:
- OpenAPI (Swagger): http://localhost:8000/api/schema/swagger-ui/
- ReDoc: http://localhost:8000/api/schema/redoc/

## Contributing

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to contribute to this project.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

If you have any questions or need help, please open an issue on GitHub.
