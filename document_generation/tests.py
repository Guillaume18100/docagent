from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import DocumentTemplate, GeneratedDocument
from document_processing.models import Document

class DocumentTemplateTests(TestCase):
    """Tests for the DocumentTemplate model and API"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create a test template
        self.template = DocumentTemplate.objects.create(
            name="Test Template",
            description="A test template",
            template_content="This is a test template with {{variable}}.",
            variables={"variable": "example value"}
        )
    
    def test_template_creation(self):
        """Test creating a template"""
        self.assertEqual(DocumentTemplate.objects.count(), 1)
        self.assertEqual(self.template.name, "Test Template")
        self.assertEqual(self.template.variables["variable"], "example value")
    
    def test_list_templates(self):
        """Test listing templates"""
        url = reverse('documenttemplate-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "Test Template")

class GeneratedDocumentTests(TestCase):
    """Tests for the GeneratedDocument model and API"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create a test template
        self.template = DocumentTemplate.objects.create(
            name="Test Template",
            description="A test template",
            template_content="This is a test template.",
            variables={}
        )
        
        # Create a test document
        self.document = Document.objects.create(
            title="Test Document",
            document_type="txt",
            extracted_text="This is a test document content."
        )
        
        # Create a test generated document
        self.generated_document = GeneratedDocument.objects.create(
            title="Test Generated Document",
            template=self.template,
            content="This is a test generated document content.",
            parameters={"prompt": "Generate a test document"}
        )
        self.generated_document.source_documents.add(self.document)
    
    def test_document_creation(self):
        """Test creating a generated document"""
        self.assertEqual(GeneratedDocument.objects.count(), 1)
        self.assertEqual(self.generated_document.title, "Test Generated Document")
        self.assertEqual(self.generated_document.template, self.template)
        self.assertEqual(self.generated_document.source_documents.count(), 1)
    
    def test_list_documents(self):
        """Test listing generated documents"""
        url = reverse('generateddocument-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], "Test Generated Document") 