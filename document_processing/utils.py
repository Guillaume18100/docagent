import os
import pytesseract
from PIL import Image
import tika
from tika import parser
from pdf2image import convert_from_path
import docx
import logging
from django.conf import settings

# Initialize tika
tika.initVM()

# Configure logging
logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_path):
    """
    Extract text from PDF using Tika
    
    Args:
        file_path (str): Path to the PDF file
        
    Returns:
        tuple: (extracted_text, metadata)
    """
    try:
        parsed = parser.from_file(file_path)
        text = parsed.get('content', '')
        metadata = parsed.get('metadata', {})
        
        # If text extraction failed or returned very little text, try OCR
        if not text or len(text.strip()) < 100:
            logger.info(f"Tika extracted minimal text from {file_path}, trying OCR")
            return extract_text_from_pdf_with_ocr(file_path)
            
        return text, metadata
    except Exception as e:
        logger.error(f"Error extracting text from PDF {file_path}: {str(e)}")
        return "", {}

def extract_text_from_pdf_with_ocr(file_path):
    """
    Extract text from PDF using OCR when Tika fails
    
    Args:
        file_path (str): Path to the PDF file
        
    Returns:
        tuple: (extracted_text, metadata)
    """
    try:
        # Convert PDF to images
        images = convert_from_path(file_path)
        
        # Extract text from each image
        text = ""
        for i, image in enumerate(images):
            temp_img_path = f"/tmp/page_{i}.png"
            image.save(temp_img_path, 'PNG')
            
            # Extract text using pytesseract
            page_text = pytesseract.image_to_string(Image.open(temp_img_path))
            text += f"\n\n--- Page {i+1} ---\n\n{page_text}"
            
            # Clean up temporary file
            os.remove(temp_img_path)
            
        return text, {"ocr_processed": True}
    except Exception as e:
        logger.error(f"Error extracting text from PDF with OCR {file_path}: {str(e)}")
        return "", {"ocr_error": str(e)}

def extract_text_from_docx(file_path):
    """
    Extract text from DOCX file
    
    Args:
        file_path (str): Path to the DOCX file
        
    Returns:
        tuple: (extracted_text, metadata)
    """
    try:
        # Try with Tika first
        parsed = parser.from_file(file_path)
        text = parsed.get('content', '')
        metadata = parsed.get('metadata', {})
        
        # If Tika fails, use python-docx as fallback
        if not text:
            logger.info(f"Tika failed to extract text from {file_path}, using python-docx")
            doc = docx.Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            metadata = {"fallback_extraction": "python-docx"}
            
        return text, metadata
    except Exception as e:
        logger.error(f"Error extracting text from DOCX {file_path}: {str(e)}")
        return "", {}

def extract_text_from_image(file_path):
    """
    Extract text from image using OCR
    
    Args:
        file_path (str): Path to the image file
        
    Returns:
        tuple: (extracted_text, metadata)
    """
    try:
        # Use pytesseract for OCR
        text = pytesseract.image_to_string(Image.open(file_path))
        metadata = {"ocr_engine": "pytesseract"}
        return text, metadata
    except Exception as e:
        logger.error(f"Error extracting text from image {file_path}: {str(e)}")
        return "", {}

def extract_text_from_txt(file_path):
    """
    Extract text from plain text file
    
    Args:
        file_path (str): Path to the text file
        
    Returns:
        tuple: (extracted_text, metadata)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
        return text, {"file_type": "text/plain"}
    except UnicodeDecodeError:
        # Try with different encoding if UTF-8 fails
        try:
            with open(file_path, 'r', encoding='latin-1') as file:
                text = file.read()
            return text, {"file_type": "text/plain", "encoding": "latin-1"}
        except Exception as e:
            logger.error(f"Error reading text file with latin-1 encoding {file_path}: {str(e)}")
            return "", {}
    except Exception as e:
        logger.error(f"Error reading text file {file_path}: {str(e)}")
        return "", {}

def process_document(document):
    """
    Process a document based on its type
    
    Args:
        document: Document model instance
        
    Returns:
        bool: True if processing was successful, False otherwise
    """
    try:
        file_path = document.file.path
        document.processing_status = 'processing'
        document.save()
        
        if document.document_type == 'pdf':
            text, metadata = extract_text_from_pdf(file_path)
        elif document.document_type == 'docx':
            text, metadata = extract_text_from_docx(file_path)
        elif document.document_type == 'image':
            text, metadata = extract_text_from_image(file_path)
        elif document.document_type == 'txt':
            text, metadata = extract_text_from_txt(file_path)
        else:
            # Try Tika for unknown file types
            parsed = parser.from_file(file_path)
            text = parsed.get('content', '')
            metadata = parsed.get('metadata', {})
        
        # Update document with extracted text and metadata
        document.extracted_text = text
        document.metadata = metadata
        document.processing_status = 'completed'
        document.save()
        
        return True
    except Exception as e:
        logger.error(f"Error processing document {document.id}: {str(e)}")
        document.processing_status = 'failed'
        document.error_message = str(e)
        document.save()
        return False 