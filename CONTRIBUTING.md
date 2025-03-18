# Contributing to DocAgent

Thank you for your interest in contributing to DocAgent! This document provides guidelines and instructions for contributing to this project.

## Development Setup

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn
- Optional: Docker and docker-compose for container-based deployment

### Setting up the Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/docagent.git
   cd docagent
   ```

2. Set up the project:
   ```bash
   make setup
   ```

   This will:
   - Set up a Python virtual environment
   - Install backend dependencies (including NLP libraries)
   - Install frontend dependencies
   - Download necessary model data

### Starting the Development Environment

The simplest way to start development is with a single command:

```bash
make start
```

This command will:
- Automatically detect the best available environment (local or Docker)
- Start all required services
- Apply database migrations
- Open the application in your browser

The application will be available at:
- Frontend: http://localhost:8080
- Backend API: http://localhost:8000/api
- Admin interface: http://localhost:8000/admin

### Alternative Start Methods

If you prefer a specific environment, you can use:

```bash
# Start in local development mode
make start-dev

# Start using Docker
make start-docker
```

## Developer Workflow for AI Analysis Feature

When working on the AI analysis feature:

1. Documents are analyzed automatically when uploaded
2. Analysis results can be viewed in the "AI Analysis" tab
3. The NLP pipeline includes:
   - Text extraction from documents
   - Summarization
   - Keyword extraction
   - Entity recognition
   - Sentiment analysis
   - Topic identification

Key files for the AI analysis feature:
- `docautomation_backend/nlp/models.py` - Database models for analysis results
- `docautomation_backend/nlp/utils.py` - NLP processing utilities
- `docautomation_backend/nlp/views.py` - API endpoints for analysis
- `src/components/DocumentAnalysisViewer.tsx` - Frontend component for displaying analysis

## Code Style and Guidelines

### Backend (Python)
- Follow PEP 8 style guidelines
- Use docstrings for functions and classes
- Write unit tests for new functionality
- Keep functions small and focused on a single task

### Frontend (React/TypeScript)
- Follow ESLint rules provided in the project
- Use TypeScript types for all components and functions
- Use functional components with hooks
- Follow the component structure established in the project

## Pull Request Process

1. Create a new branch from `main` for your feature or bug fix
2. Make your changes and commit them with clear, descriptive commit messages
3. Push your branch and submit a pull request
4. Ensure your PR description clearly describes the problem and solution
5. Reference any related issues

## Code Review Process

All submissions require review. The maintainers will review your PR and may suggest changes or improvements. 

## Testing

- Write tests for all new features or bug fixes
- Ensure all existing tests pass before submitting a PR
- For backend: Use Django's test framework
- For frontend: Use Jest/React Testing Library

## Documentation

- Update documentation when changing or adding features
- Document APIs using docstrings and OpenAPI specifications
- Maintain up-to-date README instructions

## Code of Conduct

By participating in this project, you agree to abide by the Code of Conduct. Please report unacceptable behavior to the project maintainers.

## Questions?

If you have any questions, feel free to open an issue for discussion. 