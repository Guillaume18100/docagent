from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
import os
import tempfile
from .models import Document
from .utils import extract_text_from_txt

class DocumentModelTests(TestCase):
    """Tests for the Document model"""
    
    def test_document_creation(self):
        """Test creating a document"""
        # Create a temporary text file
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp:
            temp.write(b'Test document content')
            temp_path = temp.name
        
        try:
            # Create a document
            document = Document.objects.create(
                title='Test Document',
                file=temp_path
            )
            
            # Check that the document was created
            self.assertEqual(Document.objects.count(), 1)
            self.assertEqual(document.title, 'Test Document')
            self.assertEqual(document.document_type, 'txt')
            self.assertEqual(document.processing_status, 'pending')
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def test_file_extension(self):
        """Test the file_extension method"""
        document = Document(file='test.pdf')
        self.assertEqual(document.file_extension(), 'pdf')
        
        document = Document(file='test.docx')
        self.assertEqual(document.file_extension(), 'docx')
        
        document = Document(file='test.txt')
        self.assertEqual(document.file_extension(), 'txt')
        
        document = Document(file='test.jpg')
        self.assertEqual(document.file_extension(), 'jpg')
    
    def test_determine_document_type(self):
        """Test the determine_document_type method"""
        document = Document(file='test.pdf')
        self.assertEqual(document.determine_document_type(), 'pdf')
        
        document = Document(file='test.docx')
        self.assertEqual(document.determine_document_type(), 'docx')
        
        document = Document(file='test.txt')
        self.assertEqual(document.determine_document_type(), 'txt')
        
        document = Document(file='test.jpg')
        self.assertEqual(document.determine_document_type(), 'image')
        
        document = Document(file='test.unknown')
        self.assertEqual(document.determine_document_type(), 'other')

class DocumentAPITests(TestCase):
    """Tests for the Document API"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create a test document file
        self.test_file = SimpleUploadedFile(
            "test_document.txt",
            b"This is a test document content.",
            content_type="text/plain"
        )
    
    def test_upload_document(self):
        """Test uploading a document"""
        url = reverse('document-list')
        data = {
            'title': 'Test Document',
            'file': self.test_file
        }
        
        response = self.client.post(url, data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Document.objects.count(), 1)
        self.assertEqual(Document.objects.get().title, 'Test Document')
    
    def test_list_documents(self):
        """Test listing documents"""
        # Create a test document
        Document.objects.create(
            title='Test Document',
            file=self.test_file.name,
            document_type='txt',
            processing_status='completed'
        )
        
        url = reverse('document-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Test Document')
    
    def test_retrieve_document(self):
        """Test retrieving a document"""
        # Create a test document
        document = Document.objects.create(
            title='Test Document',
            file=self.test_file.name,
            document_type='txt',
            processing_status='completed',
            extracted_text='This is the extracted text.'
        )
        
        url = reverse('document-detail', args=[document.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Document')
        self.assertEqual(response.data['extracted_text'], 'This is the extracted text.')

class DocumentUtilsTests(TestCase):
    """Tests for document processing utilities"""
    
    def test_extract_text_from_txt(self):
        """Test extracting text from a text file"""
        # Create a temporary text file
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp:
            temp.write(b'Test document content')
            temp_path = temp.name
        
        try:
            # Extract text from the file
            text, metadata = extract_text_from_txt(temp_path)
            
            # Check the extracted text
            self.assertEqual(text, 'Test document content')
            self.assertEqual(metadata['file_type'], 'text/plain')
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path) 