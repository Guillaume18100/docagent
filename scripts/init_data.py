#!/usr/bin/env python
"""
Initialize sample data for development purposes.
Run this script after setting up the database.

Example:
    python scripts/init_data.py
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to the Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR / "docautomation_backend"))

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "docautomation_backend.settings")
django.setup()

# Import models after Django setup
from django.contrib.auth.models import User
from document_processing.models import Document, DocumentType
from nlp.models import NLPAnalysis, Entity

def create_superuser():
    """Create a superuser if it doesn't exist."""
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpassword"
        )
        print("Created superuser: admin")
    else:
        print("Superuser already exists")

def create_document_types():
    """Create document types if they don't exist."""
    document_types = [
        {"name": "Invoice", "description": "Financial invoice document"},
        {"name": "Resume", "description": "Professional CV/Resume"},
        {"name": "Contract", "description": "Legal contract document"},
        {"name": "Report", "description": "Business or technical report"},
    ]
    
    for doc_type in document_types:
        DocumentType.objects.get_or_create(
            name=doc_type["name"],
            defaults={"description": doc_type["description"]}
        )
    
    print(f"Created {len(document_types)} document types")

def create_sample_documents():
    """Create sample documents if none exist."""
    if Document.objects.count() == 0:
        user = User.objects.get(username="admin")
        doc_types = DocumentType.objects.all()
        
        sample_documents = [
            {
                "title": "Sample Invoice #1",
                "doc_type": doc_types.get(name="Invoice"),
                "content": "This is a sample invoice for development purposes.",
                "user": user
            },
            {
                "title": "Sample Contract",
                "doc_type": doc_types.get(name="Contract"),
                "content": "This is a sample contract for development purposes.",
                "user": user
            },
            {
                "title": "Sample Resume",
                "doc_type": doc_types.get(name="Resume"),
                "content": "This is a sample resume for development purposes.",
                "user": user
            }
        ]
        
        for doc in sample_documents:
            Document.objects.create(**doc)
        
        print(f"Created {len(sample_documents)} sample documents")
    else:
        print("Sample documents already exist")

def create_sample_analyses():
    """Create sample NLP analyses if none exist."""
    if NLPAnalysis.objects.count() == 0:
        documents = Document.objects.all()
        
        for doc in documents:
            analysis = NLPAnalysis.objects.create(
                document=doc,
                summary="This is a sample summary for the document.",
                sentiment_score=0.75,
                language="en"
            )
            
            # Create sample entities
            Entity.objects.create(
                analysis=analysis,
                entity_type="PERSON",
                text="John Doe",
                start_pos=10,
                end_pos=18
            )
            
            Entity.objects.create(
                analysis=analysis,
                entity_type="ORG",
                text="Acme Corporation",
                start_pos=30,
                end_pos=46
            )
        
        print(f"Created {documents.count()} sample analyses with entities")
    else:
        print("Sample analyses already exist")

def main():
    """Main function to initialize all sample data."""
    print("Initializing sample data...")
    create_superuser()
    create_document_types()
    create_sample_documents()
    create_sample_analyses()
    print("Sample data initialization complete!")

if __name__ == "__main__":
    main() 