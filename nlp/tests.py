from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import UserQuery, Conversation, Message
from document_processing.models import Document
from .utils import extract_entities, generate_clarifying_questions

class UserQueryTests(TestCase):
    """Tests for the UserQuery model and API"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create a test document
        self.document = Document.objects.create(
            title="Test Document",
            document_type="txt",
            extracted_text="This is a test document content."
        )
        
        # Create a test user query
        self.user_query = UserQuery.objects.create(
            query_text="I need information about contracts",
            analyzed_result={
                "intent": "information_request",
                "entities": {
                    "document_types": ["contract"]
                },
                "clarifying_questions": [
                    "What specific information are you looking for?",
                    "Would you like me to search in any particular documents?"
                ]
            }
        )
        self.user_query.related_documents.add(self.document)
    
    def test_query_creation(self):
        """Test creating a user query"""
        self.assertEqual(UserQuery.objects.count(), 1)
        self.assertEqual(self.user_query.query_text, "I need information about contracts")
        self.assertEqual(self.user_query.related_documents.count(), 1)
    
    def test_analyze_query(self):
        """Test analyzing a user query"""
        url = reverse('userquery-list')
        data = {
            'query_text': 'I need to create a contract',
            'document_ids': [self.document.id]
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UserQuery.objects.count(), 2)
        self.assertIn('analyzed_result', response.data)

class ConversationTests(TestCase):
    """Tests for the Conversation model and API"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create a test conversation
        self.conversation = Conversation.objects.create(
            title="Test Conversation"
        )
        
        # Add messages to the conversation
        Message.objects.create(
            conversation=self.conversation,
            role="user",
            content="Hello, I need help with document automation."
        )
        
        Message.objects.create(
            conversation=self.conversation,
            role="assistant",
            content="I can help you with document automation. What specifically do you need?"
        )
    
    def test_conversation_creation(self):
        """Test creating a conversation"""
        self.assertEqual(Conversation.objects.count(), 1)
        self.assertEqual(self.conversation.title, "Test Conversation")
        self.assertEqual(self.conversation.messages.count(), 2)
    
    def test_add_message(self):
        """Test adding a message to a conversation"""
        url = reverse('conversation-add-message', args=[self.conversation.id])
        data = {
            'role': 'user',
            'content': 'I need to create a contract template.'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.conversation.messages.count(), 4)  # 2 original + 1 user + 1 assistant response
        
        # Check that the last message is from the assistant
        last_message = self.conversation.messages.last()
        self.assertEqual(last_message.role, 'assistant')

class NLPUtilsTests(TestCase):
    """Tests for NLP utility functions"""
    
    def test_extract_entities(self):
        """Test extracting entities from text"""
        text = "I need to create a contract for Acme Corporation"
        entities = extract_entities(text)
        
        self.assertIn("document_types", entities)
        self.assertIn("contract", entities["document_types"])
    
    def test_generate_clarifying_questions(self):
        """Test generating clarifying questions"""
        intent = "document_creation"
        entities = {
            "document_types": ["contract"]
        }
        
        questions = generate_clarifying_questions(intent, entities)
        
        self.assertTrue(len(questions) > 0)
        self.assertIn("Could you provide more details about the content you need in this document?", questions) 