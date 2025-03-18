import logging
import re
import os
import json
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

try:
    import nltk
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.corpus import stopwords
    
    # Download required NLTK resources
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    
    HAVE_NLTK = True
except ImportError:
    logger.warning("NLTK not available. Basic NLP features will be limited.")
    HAVE_NLTK = False

# Try to import transformers for advanced NLP
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    HAVE_TRANSFORMERS = True
except ImportError:
    logger.warning("Transformers not available. Advanced NLP features will be disabled.")
    HAVE_TRANSFORMERS = False

# Simple regex-based entity extraction fallback
def extract_entities_with_regex(text):
    """Extract entities using regex patterns when more advanced methods are unavailable"""
    entities = []
    
    # Email regex
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    for email in emails:
        entities.append({"text": email, "type": "EMAIL", "confidence": 0.9})
    
    # Phone regex
    phone_pattern = r'\b(?:\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b'
    phones = re.findall(phone_pattern, text)
    for phone in phones:
        entities.append({"text": phone, "type": "PHONE", "confidence": 0.8})
    
    # URL regex
    url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
    urls = re.findall(url_pattern, text)
    for url in urls:
        entities.append({"text": url, "type": "URL", "confidence": 0.9})
    
    # Date regex (simple)
    date_pattern = r'\b(?:\d{1,2}[-/]\d{1,2}[-/]\d{2,4})|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b'
    dates = re.findall(date_pattern, text, re.IGNORECASE)
    for date in dates:
        entities.append({"text": date, "type": "DATE", "confidence": 0.7})
    
    return entities

def simple_summarize(text, max_sentences=5):
    """Generate a simple summary when advanced methods are unavailable"""
    if not HAVE_NLTK:
        # Very basic summary - just first 2-3 sentences
        sentences = text.split('.')
        return '. '.join(sentences[:3]) + '.'
    
    # Use NLTK for slightly better summarization
    sentences = sent_tokenize(text)
    
    # Use a basic frequency-based approach
    stop_words = set(stopwords.words('english'))
    word_frequencies = {}
    
    for sentence in sentences:
        words = word_tokenize(sentence.lower())
        for word in words:
            if word not in stop_words and word.isalnum():
                if word not in word_frequencies:
                    word_frequencies[word] = 1
                else:
                    word_frequencies[word] += 1
    
    # Normalize frequencies
    if word_frequencies:
        max_frequency = max(word_frequencies.values())
        for word in word_frequencies:
            word_frequencies[word] = word_frequencies[word] / max_frequency
    
    # Score sentences based on word frequencies
    sentence_scores = {}
    for i, sentence in enumerate(sentences):
        words = word_tokenize(sentence.lower())
        score = 0
        for word in words:
            if word in word_frequencies:
                score += word_frequencies[word]
        sentence_scores[i] = score / max(1, len(words))
    
    # Get top N sentences
    summary_sentence_indices = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:max_sentences]
    summary_sentence_indices.sort()  # Sort by original order
    
    summary = ' '.join([sentences[i] for i in summary_sentence_indices])
    return summary

def extract_keywords(text, max_keywords=10):
    """Extract keywords from text"""
    if not HAVE_NLTK:
        return []
    
    # Simple keyword extraction with NLTK
    words = word_tokenize(text.lower())
    stop_words = set(stopwords.words('english'))
    
    # Filter out stopwords and non-alphanumeric words
    filtered_words = [word for word in words if word not in stop_words and word.isalnum() and len(word) > 2]
    
    # Count word frequencies
    word_freq = {}
    for word in filtered_words:
        if word in word_freq:
            word_freq[word] += 1
        else:
            word_freq[word] = 1
    
    # Get top keywords
    keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:max_keywords]
    return [{"word": k, "count": v} for k, v in keywords]

def analyze_sentiment(text):
    """Analyze sentiment of text"""
    if HAVE_TRANSFORMERS:
        try:
            # Use transformers for sentiment analysis
            sentiment_analyzer = pipeline("sentiment-analysis")
            result = sentiment_analyzer(text[:512])[0]  # Use first 512 chars to avoid token limits
            
            # Convert to -1 to 1 scale
            score = 0
            if result["label"] == "POSITIVE":
                score = result["score"]
            elif result["label"] == "NEGATIVE":
                score = -result["score"]
                
            return score
        except Exception as e:
            logger.warning(f"Error in transformer-based sentiment analysis: {e}")
    
    # Very basic sentiment analysis using positive/negative word lists
    positive_words = ['good', 'great', 'excellent', 'best', 'happy', 'positive', 'nice', 'love', 'perfect', 'recommend']
    negative_words = ['bad', 'worst', 'terrible', 'awful', 'poor', 'negative', 'hate', 'horrible', 'disappointing', 'avoid']
    
    text_lower = text.lower()
    words = re.findall(r'\b\w+\b', text_lower)
    
    positive_count = sum(1 for word in words if word in positive_words)
    negative_count = sum(1 for word in words if word in negative_words)
    
    total = positive_count + negative_count
    if total == 0:
        return 0  # Neutral
    
    return (positive_count - negative_count) / max(1, total)

def extract_entities_with_transformers(text):
    """Extract named entities using transformers"""
    if not HAVE_TRANSFORMERS:
        return []
    
    try:
        ner_pipeline = pipeline("ner")
        entities = ner_pipeline(text[:512])  # Use first 512 chars to avoid token limits
        
        # Group and format entities
        formatted_entities = []
        current_entity = None
        
        for entity in entities:
            if current_entity and current_entity["word"].endswith("##"):
                # Continue previous entity (WordPiece tokenization)
                current_entity["word"] = current_entity["word"][:-2] + entity["word"].replace("##", "")
            else:
                if current_entity:
                    # Add previous entity to results
                    formatted_entities.append({
                        "text": current_entity["word"],
                        "type": current_entity["entity"],
                        "confidence": current_entity["score"]
                    })
                
                # Start new entity
                current_entity = {
                    "word": entity["word"],
                    "entity": entity["entity"],
                    "score": entity["score"]
                }
        
        # Add last entity
        if current_entity:
            formatted_entities.append({
                "text": current_entity["word"],
                "type": current_entity["entity"],
                "confidence": current_entity["score"]
            })
            
        return formatted_entities
    except Exception as e:
        logger.warning(f"Error in transformer-based entity extraction: {e}")
        return []

def analyze_document(document):
    """
    Analyze a document using NLP techniques
    
    Args:
        document: Document model instance
        
    Returns:
        dict: Analysis results
    """
    try:
        logger.info(f"Analyzing document: {document.title}")
        
        # Check if document has extracted text
        if not document.extracted_text:
            logger.warning(f"Document {document.id} has no extracted text to analyze")
            return {
                "success": False,
                "error": "Document has no extracted text"
            }
        
        text = document.extracted_text
        
        # Generate summary
        if HAVE_TRANSFORMERS:
            try:
                summarizer = pipeline("summarization")
                
                # Split text into chunks to handle long documents
                max_chunk_size = 1000
                chunks = [text[i:i+max_chunk_size] for i in range(0, len(text), max_chunk_size)]
                
                summary_chunks = []
                for chunk in chunks[:3]:  # Process up to 3 chunks to avoid excessive processing
                    if len(chunk) < 50:  # Skip very small chunks
                        continue
                    result = summarizer(chunk, max_length=100, min_length=30, do_sample=False)
                    if result and result[0]['summary_text']:
                        summary_chunks.append(result[0]['summary_text'])
                
                summary = " ".join(summary_chunks)
                if not summary:
                    summary = simple_summarize(text)
            except Exception as e:
                logger.warning(f"Error in transformer-based summarization: {e}")
                summary = simple_summarize(text)
        else:
            summary = simple_summarize(text)
        
        # Extract keywords
        keywords = extract_keywords(text)
        
        # Analyze sentiment
        sentiment = analyze_sentiment(text)
        
        # Extract entities
        if HAVE_TRANSFORMERS:
            entities = extract_entities_with_transformers(text)
            if not entities:
                entities = extract_entities_with_regex(text)
        else:
            entities = extract_entities_with_regex(text)
        
        # Extract topics (simplified)
        topics = []
        if keywords:
            topics = [{"topic": kw["word"], "score": 1.0 - idx/len(keywords)} for idx, kw in enumerate(keywords[:3])]
        
        # Prepare analysis results
        analysis_results = {
            "summary": summary,
            "keywords": keywords,
            "sentiment": sentiment,
            "entities": entities,
            "topics": topics,
        }
        
        return {
            "success": True,
            "results": analysis_results
        }
    except Exception as e:
        logger.error(f"Error analyzing document {document.id}: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        } 