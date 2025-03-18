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
- LangChain
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
- Tesseract OCR (for document processing)

### Installation

#### Option 1: Simple Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/docagent.git
cd docagent

# Run the setup script
chmod +x setup.sh
./setup.sh
```

#### Option 2: Using Make

```bash
# Clone the repository
git clone https://github.com/yourusername/docagent.git
cd docagent

# Run the setup command
make setup
```

#### Option 3: Using Docker

```bash
# Clone the repository
git clone https://github.com/yourusername/docagent.git
cd docagent

# Build and start the containers
docker-compose up -d
```

### Running the Application

#### Local Development

Start the backend server:
```bash
cd docautomation_backend
source venv/bin/activate
python manage.py runserver
```

Start the frontend development server:
```bash
cd src
npm run dev
```

#### Using Make

```bash
# Run backend
make run-backend

# In another terminal, run frontend
make run-frontend
```

#### Using Docker

```bash
docker-compose up
```

The application will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/api
- Admin interface: http://localhost:8000/admin (username: admin, password: adminpassword)

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
│   └── lib/                 # Utility functions
├── scripts/                 # Utility scripts
├── .env                     # Environment variables
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
