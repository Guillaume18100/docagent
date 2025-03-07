from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
import json
import os
import traceback
from datetime import datetime
import threading
import uuid

# Import document model
from document_processing.models import Document

# Flag to check if HF transformers is available
TRANSFORMERS_AVAILABLE = False
GPT_MODEL = None
TOKENIZER = None

# Try to import and initialize transformers
try:
    from transformers import GPT2LMHeadModel, GPT2Tokenizer, pipeline
    
    # Initialize in a separate thread to avoid blocking
    def initialize_models():
        global TRANSFORMERS_AVAILABLE, GPT_MODEL, TOKENIZER
        
        try:
            print("Initializing Hugging Face Transformers models...")
            # Load the model and tokenizer
            model_name = "gpt2"  # Can be changed to a fine-tuned model
            
            # Load tokenizer and model with proper pipeline for text generation
            TOKENIZER = GPT2Tokenizer.from_pretrained(model_name)
            GPT_MODEL = GPT2LMHeadModel.from_pretrained(model_name)
            
            TRANSFORMERS_AVAILABLE = True
            print("Hugging Face models initialized successfully!")
        except Exception as e:
            print(f"Error initializing Transformers models: {str(e)}")
            traceback.print_exc()
    
    # Start initialization in background
    threading.Thread(target=initialize_models).start()
    
except ImportError:
    print("Hugging Face Transformers not available. Install with: pip install transformers torch")

# Mock conversation data for development
MOCK_CONVERSATIONS = []

@api_view(['GET'])
@permission_classes([AllowAny])
def conversation_list(request):
    """
    List conversations for a document or all conversations
    """
    print("Conversation list endpoint called")
    document_id = request.query_params.get('document_id')
    
    # For development, return mock data or an empty list
    if document_id:
        # Filter by document ID if provided
        conversations = [c for c in MOCK_CONVERSATIONS if c.get('document_id') == document_id]
        return Response(conversations)
    else:
        return Response(MOCK_CONVERSATIONS)

@api_view(['POST'])
@permission_classes([AllowAny])
def analyze_query(request):
    """
    Analyze a user query against document(s) and generate clarifying questions
    """
    print("Analyze query endpoint called")
    try:
        data = request.data
        print(f"Query data: {data}")
        
        query_text = data.get('query_text', '')
        document_ids = data.get('document_ids', [])
        
        if not query_text:
            return Response(
                {'error': 'No query text provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        print(f"Processing query: {query_text}")
        print(f"For documents: {document_ids}")
        
        # Get document texts if document IDs are provided
        document_texts = []
        documents = []
        for doc_id in document_ids:
            try:
                document = Document.objects.get(id=doc_id)
                documents.append(document)
                if document.extracted_text:
                    document_texts.append({
                        'id': doc_id,
                        'title': document.title,
                        'text': document.extracted_text[:1000]  # Use first 1000 chars
                    })
            except Document.DoesNotExist:
                pass
        
        # Check if this is a document generation request
        generation_requested = False
        generation_response = ""
        
        # Look for generation keywords
        generation_keywords = ['create', 'generate', 'make', 'produce', 'write', 'draft']
        document_keywords = ['document', 'file', 'pdf', 'docx', 'text', 'report', 'letter', 'draft']
        
        if any(keyword in query_text.lower() for keyword in generation_keywords) and \
           any(keyword in query_text.lower() for keyword in document_keywords):
            
            # This appears to be a document generation request
            print("Document generation request detected")
            generation_requested = True
            
            # Determine output format
            output_format = 'docx'  # default
            if 'pdf' in query_text.lower():
                output_format = 'pdf'
            elif 'text' in query_text.lower() or 'txt' in query_text.lower():
                output_format = 'txt'
            elif 'markdown' in query_text.lower() or 'md' in query_text.lower():
                output_format = 'markdown'
            elif 'html' in query_text.lower():
                output_format = 'html'
            
            # Extract a title for the document
            title = f"Generated Document - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            # Look for "for [subject]" pattern
            if 'for' in query_text.lower():
                parts = query_text.lower().split('for')
                if len(parts) > 1:
                    subject_part = parts[1].strip()
                    # Extract the first few words after "for"
                    subject_words = subject_part.split()[:3]  # Take up to 3 words
                    subject = ' '.join(subject_words).strip().capitalize()
                    if subject:
                        title = f"Document for {subject}"
            
            # If we have reference documents, use the first one's title as a base
            if documents:
                ref_doc = documents[0]
                ref_title = ref_doc.title
                
                # Try to extract location names
                if 'same' in query_text.lower() and 'for' in query_text.lower():
                    # Get original title
                    original_title = ref_title
                    
                    # Try to find the new location
                    parts = query_text.lower().split('for')
                    if len(parts) > 1:
                        new_location = parts[1].strip().split()[0].capitalize()
                        
                        # Replace the location in the original title if possible
                        # This is a simple approach - might need to be more sophisticated
                        for word in original_title.split():
                            if len(word) > 3:  # Avoid replacing short words
                                # Create a new title with the location replaced
                                title = original_title.replace(word, new_location)
                                if title != original_title:
                                    break
            
            try:
                # Prepare data for document generation
                generation_data = {
                    'title': title,
                    'prompt': query_text,
                    'output_format': output_format,
                    'document_ids': document_ids
                }
                
                # Import inside the function to avoid circular imports
                from document_generation.models import GeneratedDocument
                from document_generation.views import generate_document
                
                # Create the generated document
                generated_doc = GeneratedDocument(
                    title=title,
                    prompt=query_text,
                    output_format=output_format,
                    status='pending'
                )
                generated_doc.save()
                
                # Add reference documents
                if document_ids:
                    for doc_id in document_ids:
                        try:
                            doc = Document.objects.get(id=doc_id)
                            generated_doc.reference_documents.add(doc)
                        except Document.DoesNotExist:
                            pass
                
                # Start generation in background thread
                import threading
                threading.Thread(target=generate_document, args=(generated_doc,)).start()
                
                generation_response = (
                    f"I've started generating a new {output_format.upper()} document titled '{title}' "
                    f"based on your request. You can view the status and download it when ready "
                    f"in the 'Generate Documents' tab."
                )
                
                print(f"Document generation started. ID: {generated_doc.id}")
                
            except Exception as e:
                print(f"Error initiating document generation: {str(e)}")
                traceback.print_exc()
                generation_response = f"I tried to generate a document based on your request, but encountered an error: {str(e)}"
        
        # Generate response based on the query and documents
        ai_response = generate_ai_response(query_text, document_texts)
        
        # If this is a document generation request, handle it specially
        if generation_requested and generation_response:
            ai_response = generation_response + "\n\n" + ai_response
        
        # Create response with user message and system response
        current_time = datetime.now().isoformat()
        user_message_id = f"user-{uuid.uuid4()}"
        system_message_id = f"system-{uuid.uuid4()}"
        
        # Add to mock conversation history
        if document_ids:
            doc_id = document_ids[0]
            conversation = next((c for c in MOCK_CONVERSATIONS if c.get('document_id') == doc_id), None)
            
            if not conversation:
                conversation = {
                    'id': str(uuid.uuid4()),
                    'document_id': doc_id,
                    'messages': []
                }
                MOCK_CONVERSATIONS.append(conversation)
                
            # Add user message
            conversation['messages'].append({
                'id': user_message_id,
                'content': query_text,
                'sender': 'user',
                'timestamp': current_time
            })
            
            # Add system response
            conversation['messages'].append({
                'id': system_message_id,
                'content': ai_response,
                'sender': 'system',
                'timestamp': current_time
            })
        
        # Create response objects
        response = {
            'userMessage': {
                'id': user_message_id,
                'document_id': document_ids[0] if document_ids else None,
                'content': query_text,
                'sender': 'user',
                'timestamp': current_time
            },
            'systemResponse': {
                'id': system_message_id,
                'document_id': document_ids[0] if document_ids else None,
                'content': ai_response,
                'sender': 'system',
                'timestamp': current_time
            },
            'clarifyingQuestions': extract_questions(ai_response),
            'documentGenerated': generation_requested
        }
        
        return Response(response)
        
    except Exception as e:
        print(f"Error in analyze query: {str(e)}")
        traceback.print_exc()
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def generate_ai_response(query, document_texts=None):
    """
    Generate an AI response to the user query based on document content
    """
    # Use HuggingFace Transformers if available
    if TRANSFORMERS_AVAILABLE and GPT_MODEL and TOKENIZER:
        try:
            # First, try to determine the type of query
            query_type = determine_query_type(query)
            
            # Prepare the appropriate prompt based on query type
            if query_type == "question":
                prompt = prepare_question_prompt(query, document_texts)
            elif query_type == "summarize":
                prompt = prepare_summary_prompt(query, document_texts)
            else:
                # General response prompt
                prompt = prepare_general_prompt(query, document_texts)
            
            # Generate text with GPT-2
            input_ids = TOKENIZER.encode(prompt, return_tensors='pt')
            
            # Generate with parameters
            output = GPT_MODEL.generate(
                input_ids,
                max_length=300,  # Increased max length for more detailed responses
                num_return_sequences=1,
                temperature=0.8,
                top_k=50,
                top_p=0.92,
                do_sample=True,
                pad_token_id=TOKENIZER.eos_token_id
            )
            
            # Decode the output
            generated_text = TOKENIZER.decode(output[0], skip_special_tokens=True)
            
            # Extract just the generated response (remove the prompt)
            response_text = generated_text[len(prompt):]
            
            # Clean up and format the response
            return format_ai_response(response_text, query_type)
            
        except Exception as e:
            print(f"Error generating with Transformers: {str(e)}")
            traceback.print_exc()
            return generate_fallback_response(query, document_texts)
    else:
        # Fallback when HuggingFace is not available
        return generate_fallback_response(query, document_texts)

def determine_query_type(query):
    """Determine the type of query"""
    query_lower = query.lower()
    
    # Check for question patterns
    if "?" in query or any(word in query_lower for word in ["what", "how", "why", "who", "when", "where"]):
        return "question"
    
    # Check for summarization requests
    if any(word in query_lower for word in ["summarize", "summary", "overview", "brief"]):
        return "summarize"
    
    # Default to general response
    return "general"

def prepare_question_prompt(query, document_texts):
    """Prepare a prompt for answering a question"""
    if document_texts:
        # Combine relevant document text
        doc_text = ""
        for doc in document_texts:
            doc_text += f"\n\n{doc['text'][:1000]}"
        
        prompt = f"Based on the following document:\n{doc_text}\n\nAnswer this question: {query}\n\n"
    else:
        prompt = f"Answer this question: {query}\n\n"
    
    return prompt

def prepare_summary_prompt(query, document_texts):
    """Prepare a prompt for summarizing documents"""
    if document_texts:
        # Combine relevant document text
        doc_text = ""
        for doc in document_texts:
            doc_text += f"\n\n{doc['text'][:1000]}"
        
        prompt = f"Summarize the following document:\n{doc_text}\n\nSummary:"
    else:
        prompt = f"I don't have enough information to summarize. Please provide more context.\n\n"
    
    return prompt

def prepare_general_prompt(query, document_texts):
    """Prepare a general response prompt"""
    if document_texts:
        # Combine relevant document text
        doc_text = ""
        for doc in document_texts:
            doc_text += f"\n\n{doc['text'][:800]}"
        
        prompt = f"Document: {doc_text}\n\nUser request: {query}\n\nResponse:"
    else:
        prompt = f"User request: {query}\n\nResponse:"
    
    return prompt

def format_ai_response(text, query_type):
    """Format the AI response based on query type"""
    # Clean up whitespace
    text = text.strip()
    
    # Add appropriate prefix based on query type
    if query_type == "question":
        if not text:
            text = "I'm not sure I have enough information to answer that question accurately."
        elif len(text) < 50:
            # If response is very short, add more context
            text = f"Based on the information provided, {text}"
    
    elif query_type == "summarize":
        if not text:
            text = "I couldn't generate a proper summary with the available information."
        else:
            # Ensure it looks like a summary
            if not text.startswith("This document"):
                text = "This document " + text
    
    # Add a friendly closing for all responses
    if len(text) > 0 and not text.endswith("?"):
        text += "\n\nIs there anything else you'd like to know about this document?"
    
    return text

def generate_fallback_response(query, document_texts=None):
    """Generate a fallback response when AI models are unavailable"""
    query_lower = query.lower()
    
    if document_texts:
        doc_info = f" about '{document_texts[0]['title']}'" if document_texts else ""
        
        # Check for common query types and provide relevant responses
        if "summarize" in query_lower or "summary" in query_lower:
            return f"I've analyzed the document{doc_info}. Here's a brief summary:\n\n" + \
                   f"The document appears to be " + \
                   f"{document_texts[0]['text'][:100]}...\n\n" + \
                   "Would you like more specific information about any section?"
        
        elif "?" in query:
            return f"Based on the document{doc_info}, I can provide the following information:\n\n" + \
                   f"The document contains information about " + \
                   f"{document_texts[0]['text'][:150]}...\n\n" + \
                   "Does this help answer your question, or would you like more specific details?"
        
        else:
            return f"I've reviewed the document{doc_info}. It contains information about " + \
                   f"{document_texts[0]['text'][:200]}...\n\n" + \
                   "What specific aspects would you like me to focus on?"
    else:
        return "I don't have enough context to provide a specific response. Could you upload a document or provide more details about what you're looking for?"

def generate_fallback_questions(query, document_texts=None):
    """
    Generate fallback clarifying questions when HuggingFace is not available
    """
    # Extract key terms from the query
    words = query.lower().split()
    
    # Template questions based on common document needs
    questions = []
    
    # Document type questions
    if any(word in words for word in ['document', 'create', 'make', 'generate']):
        questions.append("What specific type of document do you need (e.g., report, proposal, legal agreement)?")
    
    # Audience questions
    questions.append("Who is the intended audience for this document?")
    
    # Purpose questions
    questions.append("What is the primary purpose or goal of this document?")
    
    # Length/structure questions
    questions.append("Do you have specific length requirements or structural elements needed?")
    
    # Tone questions
    questions.append("What tone should the document have (formal, conversational, technical)?")
    
    # Format questions
    questions.append("Do you have any specific formatting requirements?")
    
    # Return formatted questions
    result = "I'll need some additional information to create the document you want:\n\n"
    result += "\n\n".join([f"{i+1}. {q}" for i, q in enumerate(questions)])
    
    return result

def format_questions(questions_text):
    """Format the clarifying questions nicely"""
    lines = questions_text.split('\n')
    formatted_lines = []
    
    for line in lines:
        line = line.strip()
        if line and (line[0].isdigit() or line.startswith('-')):
            formatted_lines.append(line)
        elif formatted_lines:
            formatted_lines[-1] += " " + line
    
    result = "To better understand your requirements, I'd like to ask:\n\n"
    result += "\n\n".join(formatted_lines)
    
    return result

def extract_questions(text):
    """Extract individual questions from text format"""
    lines = text.split('\n')
    questions = []
    
    for line in lines:
        line = line.strip()
        if line and (line[0].isdigit() or line.startswith('-')):
            # Remove number/bullet and clean up
            question = line[2:] if line[1] in ['.', ' ', ')'] else line[1:]
            questions.append(question.strip())
    
    return questions

# Keep the generate_clarifying_questions function for backward compatibility
def generate_clarifying_questions(query, document_texts=None):
    """
    Generate clarifying questions based on the user query and document content
    Now just a wrapper around generate_ai_response with additional formatting
    """
    response = generate_ai_response(query, document_texts)
    
    # Add clarifying questions if none seem to be present
    if "?" not in response:
        questions = generate_fallback_questions(query, document_texts)
        response += "\n\n" + questions
    
    return response
