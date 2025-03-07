import logging
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, AutoModelForQuestionAnswering, pipeline
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer, util
import numpy as np

# Configure logging
logger = logging.getLogger(__name__)

# Global variables to store loaded models
INTENT_MODEL = None
INTENT_TOKENIZER = None
QA_PIPELINE = None
EMBEDDING_MODEL = None

def load_intent_model():
    """
    Load the intent classification model
    
    Returns:
        tuple: (model, tokenizer)
    """
    global INTENT_MODEL, INTENT_TOKENIZER
    
    if INTENT_MODEL is None or INTENT_TOKENIZER is None:
        try:
            # Load a pre-trained model for intent classification
            # Using a smaller BERT model for efficiency
            model_name = "distilbert-base-uncased-finetuned-sst-2-english"
            INTENT_TOKENIZER = AutoTokenizer.from_pretrained(model_name)
            INTENT_MODEL = AutoModelForSequenceClassification.from_pretrained(model_name)
            logger.info(f"Loaded intent classification model: {model_name}")
        except Exception as e:
            logger.error(f"Error loading intent classification model: {str(e)}")
            raise
    
    return INTENT_MODEL, INTENT_TOKENIZER

def load_qa_pipeline():
    """
    Load the question answering pipeline
    
    Returns:
        pipeline: Hugging Face QA pipeline
    """
    global QA_PIPELINE
    
    if QA_PIPELINE is None:
        try:
            # Load a pre-trained model for question answering
            model_name = "distilbert-base-cased-distilled-squad"
            QA_PIPELINE = pipeline("question-answering", model=model_name)
            logger.info(f"Loaded QA pipeline with model: {model_name}")
        except Exception as e:
            logger.error(f"Error loading QA pipeline: {str(e)}")
            raise
    
    return QA_PIPELINE

def load_embedding_model():
    """
    Load the sentence embedding model
    
    Returns:
        SentenceTransformer: Model for generating embeddings
    """
    global EMBEDDING_MODEL
    
    if EMBEDDING_MODEL is None:
        try:
            # Load a pre-trained model for sentence embeddings
            model_name = "all-MiniLM-L6-v2"
            EMBEDDING_MODEL = SentenceTransformer(model_name)
            logger.info(f"Loaded embedding model: {model_name}")
        except Exception as e:
            logger.error(f"Error loading embedding model: {str(e)}")
            raise
    
    return EMBEDDING_MODEL

def analyze_user_query(query_text):
    """
    Analyze user query to determine intent and extract key information
    
    Args:
        query_text (str): The user's query text
        
    Returns:
        dict: Analysis results including intent and extracted entities
    """
    try:
        # Load models
        model, tokenizer = load_intent_model()
        
        # Tokenize and get model prediction
        inputs = tokenizer(query_text, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            outputs = model(**inputs)
        
        # Get predicted class (positive/negative sentiment as a simple proxy for intent)
        # In a real application, you would use a model trained on your specific intents
        logits = outputs.logits
        predicted_class = torch.argmax(logits, dim=1).item()
        
        # Map the predicted class to an intent (this is a simplified example)
        intent_mapping = {
            0: "information_request",
            1: "document_creation"
        }
        
        intent = intent_mapping.get(predicted_class, "unknown")
        
        # Extract entities (simplified implementation)
        # In a real application, you would use a named entity recognition model
        entities = extract_entities(query_text)
        
        # Generate clarifying questions based on the intent and entities
        clarifying_questions = generate_clarifying_questions(intent, entities)
        
        return {
            "intent": intent,
            "entities": entities,
            "clarifying_questions": clarifying_questions,
            "confidence": torch.softmax(logits, dim=1)[0][predicted_class].item()
        }
    except Exception as e:
        logger.error(f"Error analyzing user query: {str(e)}")
        return {
            "intent": "unknown",
            "entities": [],
            "clarifying_questions": ["Could you please provide more details about your request?"],
            "error": str(e)
        }

def extract_entities(text):
    """
    Extract entities from text (simplified implementation)
    
    Args:
        text (str): Input text
        
    Returns:
        dict: Extracted entities
    """
    # This is a simplified implementation
    # In a real application, you would use a named entity recognition model
    
    entities = {
        "document_types": [],
        "dates": [],
        "organizations": [],
        "people": []
    }
    
    # Simple keyword matching for document types
    document_types = ["contract", "agreement", "letter", "memo", "report", "proposal"]
    for doc_type in document_types:
        if doc_type in text.lower():
            entities["document_types"].append(doc_type)
    
    return entities

def generate_clarifying_questions(intent, entities):
    """
    Generate clarifying questions based on intent and entities
    
    Args:
        intent (str): The identified intent
        entities (dict): Extracted entities
        
    Returns:
        list: List of clarifying questions
    """
    questions = []
    
    if intent == "document_creation":
        if not entities.get("document_types"):
            questions.append("What type of document would you like to create?")
        
        questions.append("Could you provide more details about the content you need in this document?")
        questions.append("Is there a specific format or template you'd like to use?")
    
    elif intent == "information_request":
        questions.append("What specific information are you looking for?")
        questions.append("Would you like me to search in any particular documents?")
    
    else:
        questions.append("Could you please clarify what you're looking for?")
        questions.append("Are you looking to create a document or extract information from existing documents?")
    
    return questions

def find_relevant_document_sections(query_text, documents, top_k=3):
    """
    Find the most relevant sections in the documents for the query
    
    Args:
        query_text (str): The user's query
        documents (list): List of Document objects
        top_k (int): Number of top sections to return
        
    Returns:
        list: List of relevant document sections with metadata
    """
    try:
        # Load embedding model
        model = load_embedding_model()
        
        # Create text splitter for chunking documents
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
        # Process all documents
        all_chunks = []
        for doc in documents:
            if not doc.extracted_text:
                continue
                
            chunks = text_splitter.split_text(doc.extracted_text)
            for i, chunk in enumerate(chunks):
                all_chunks.append({
                    "text": chunk,
                    "document_id": doc.id,
                    "document_title": doc.title,
                    "chunk_id": i
                })
        
        if not all_chunks:
            return []
        
        # Create embeddings for the query and all chunks
        query_embedding = model.encode(query_text, convert_to_tensor=True)
        chunk_texts = [chunk["text"] for chunk in all_chunks]
        chunk_embeddings = model.encode(chunk_texts, convert_to_tensor=True)
        
        # Calculate cosine similarities
        cos_scores = util.cos_sim(query_embedding, chunk_embeddings)[0]
        
        # Get top-k chunks
        top_results = torch.topk(cos_scores, min(top_k, len(all_chunks)))
        
        results = []
        for score, idx in zip(top_results[0], top_results[1]):
            results.append({
                "text": all_chunks[idx]["text"],
                "document_id": all_chunks[idx]["document_id"],
                "document_title": all_chunks[idx]["document_title"],
                "chunk_id": all_chunks[idx]["chunk_id"],
                "score": score.item()
            })
        
        return results
    except Exception as e:
        logger.error(f"Error finding relevant document sections: {str(e)}")
        return []

def answer_question(question, context):
    """
    Answer a question based on the provided context
    
    Args:
        question (str): The question to answer
        context (str): The context to use for answering
        
    Returns:
        dict: Answer with metadata
    """
    try:
        # Load QA pipeline
        qa_pipeline = load_qa_pipeline()
        
        # Get answer
        result = qa_pipeline(question=question, context=context)
        
        return {
            "answer": result["answer"],
            "score": result["score"],
            "start": result["start"],
            "end": result["end"]
        }
    except Exception as e:
        logger.error(f"Error answering question: {str(e)}")
        return {
            "answer": "I couldn't find an answer to your question in the provided context.",
            "error": str(e)
        } 