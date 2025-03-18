# Contributing to DocAgent

Thank you for your interest in contributing to DocAgent! This document provides guidelines and instructions for contributing to this project.

## Development Setup

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn

### Setting up the Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/docagent.git
   cd docagent
   ```

2. Run the setup script:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

   This script will:
   - Set up a Python virtual environment
   - Install backend dependencies
   - Set up the database and create a superuser
   - Install frontend dependencies
   - Build the frontend

### Starting the Development Servers

#### Backend Server
```bash
cd docautomation_backend
source venv/bin/activate
python manage.py runserver
```

#### Frontend Server
```bash
cd src
npm run dev
```

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
- For backend: Use pytest
- For frontend: Use Jest/React Testing Library

## Documentation

- Update documentation when changing or adding features
- Document APIs using docstrings and OpenAPI specifications
- Maintain up-to-date README instructions

## Code of Conduct

By participating in this project, you agree to abide by the Code of Conduct. Please report unacceptable behavior to the project maintainers.

## Questions?

If you have any questions, feel free to open an issue for discussion. 