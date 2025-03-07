import os
import logging
import threading
import traceback
import tempfile
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

# Try to import optional dependencies
try:
    import pytesseract
    from PIL import Image
    HAVE_TESSERACT = True
    TESSERACT_AVAILABLE = True
except ImportError:
    logger.warning("pytesseract or PIL not available. OCR features will be disabled.")
    HAVE_TESSERACT = False
    TESSERACT_AVAILABLE = False
    print("Tesseract OCR not available. Install with: pip install pytesseract")
    print("Also ensure Tesseract is installed on your system")

try:
    import tika
    from tika import parser
    # Initialize tika
    tika.initVM()
    HAVE_TIKA = True
    TIKA_AVAILABLE = True
except ImportError:
    logger.warning("tika-python not available. Full-text extraction from PDFs and Office documents will be limited.")
    HAVE_TIKA = False
    TIKA_AVAILABLE = False
    print("Apache Tika not available. Install with: pip install tika")

try:
    from pdf2image import convert_from_path
    HAVE_PDF2IMAGE = True
except ImportError:
    logger.warning("pdf2image not available. PDF OCR capabilities will be limited.")
    HAVE_PDF2IMAGE = False

try:
    import docx
    HAVE_DOCX = True
except ImportError:
    logger.warning("python-docx not available. DOCX extraction capabilities will be limited.")
    HAVE_DOCX = False

# Enhanced text extraction with OCR and Tika
def extract_text_from_document(file_path):
    """
    Extract text from a document using appropriate tools based on file type
    """
    print(f"Extracting text from: {file_path}")
    
    # Get file extension
    _, file_extension = os.path.splitext(file_path)
    file_extension = file_extension.lower()
    
    extracted_text = ""
    
    try:
        # Use Tika for structured documents if available
        if TIKA_AVAILABLE:
            try:
                print("Attempting text extraction with Apache Tika")
                parsed = parser.from_file(file_path)
                if parsed.get("content"):
                    extracted_text = parsed["content"]
                    print(f"Successfully extracted {len(extracted_text)} chars with Tika")
                    
                    # If text is very short, might be a scanned document, try OCR
                    if len(extracted_text.strip()) < 100 and HAVE_TESSERACT:
                        print("Short text detected, trying OCR as fallback")
                        ocr_text = perform_ocr(file_path)
                        if len(ocr_text.strip()) > len(extracted_text.strip()):
                            extracted_text = ocr_text
                            print(f"Using OCR result instead ({len(extracted_text)} chars)")
            except Exception as e:
                print(f"Tika extraction failed: {str(e)}")
                # Fall back to OCR if Tika fails
                if HAVE_TESSERACT:
                    extracted_text = perform_ocr(file_path)
        
        # If no text extracted and OCR is available, try OCR
        if not extracted_text and HAVE_TESSERACT:
            extracted_text = perform_ocr(file_path)
        
        # Fallback to basic text extraction if nothing else worked
        if not extracted_text:
            print("Falling back to basic text extraction")
            extracted_text = basic_text_extraction(file_path, file_extension)
        
        return extracted_text.strip()
    
    except Exception as e:
        print(f"Error extracting text: {str(e)}")
        traceback.print_exc()
        return ""

def perform_ocr(file_path):
    """
    Perform OCR on an image or PDF using Tesseract
    """
    if not HAVE_TESSERACT:
        return ""
    
    try:
        print("Attempting OCR with Tesseract")
        import pdf2image
        
        _, file_extension = os.path.splitext(file_path)
        file_extension = file_extension.lower()
        
        if file_extension == '.pdf':
            print("Converting PDF to images for OCR")
            # For PDFs, convert to images first
            pages = convert_from_path(file_path)
            text = ""
            
            for i, page in enumerate(pages):
                print(f"Processing page {i+1}/{len(pages)}")
                # Save temp image
                with tempfile.NamedTemporaryFile(suffix='.jpg') as temp:
                    page.save(temp.name, 'JPEG')
                    # Extract text from image
                    page_text = pytesseract.image_to_string(Image.open(temp.name))
                    text += page_text + "\n\n"
                    
            print(f"OCR complete, extracted {len(text)} chars")
            return text
        
        elif file_extension in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']:
            print("Processing image with OCR")
            # For images, use OCR directly
            text = pytesseract.image_to_string(Image.open(file_path))
            print(f"OCR complete, extracted {len(text)} chars")
            return text
        
        return ""
        
    except Exception as e:
        print(f"OCR processing error: {str(e)}")
        traceback.print_exc()
        return ""

def basic_text_extraction(file_path, file_extension):
    """
    Basic text extraction for common file types
    """
    try:
        # Handle text files
        if file_extension == '.txt':
            with open(file_path, 'r', errors='ignore') as f:
                return f.read()
                
        # For other file types, try simple methods
        elif file_extension == '.docx':
            try:
                doc = docx.Document(file_path)
                return "\n".join([para.text for para in doc.paragraphs])
            except ImportError:
                print("python-docx not available. Install with: pip install python-docx")
                
        elif file_extension == '.pdf':
            try:
                import PyPDF2
                with open(file_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
                    return text
            except ImportError:
                print("PyPDF2 not available. Install with: pip install PyPDF2")
                
        return ""
        
    except Exception as e:
        print(f"Basic extraction error: {str(e)}")
        traceback.print_exc()
        return ""

def extract_text_from_pdf(file_path):
    """
    Extract text from PDF using Tika or fallback methods
    
    Args:
        file_path (str): Path to the PDF file
        
    Returns:
        tuple: (extracted_text, metadata)
    """
    try:
        if HAVE_TIKA:
            parsed = parser.from_file(file_path)
            text = parsed.get('content', '')
            metadata = parsed.get('metadata', {})
            
            # If text extraction failed or returned very little text, try OCR
            if not text or len(text.strip()) < 100:
                logger.info(f"Tika extracted minimal text from {file_path}, trying OCR")
                if HAVE_TESSERACT and HAVE_PDF2IMAGE:
                    return extract_text_from_pdf_with_ocr(file_path)
                else:
                    logger.warning("OCR fallback not available - missing dependencies")
                
            return text, metadata
        else:
            # Simple fallback if tika is not available
            logger.warning("Using simple text extraction - Tika not available")
            return f"Text extraction not available for {os.path.basename(file_path)}", {}
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
    if not (HAVE_TESSERACT and HAVE_PDF2IMAGE):
        return "OCR processing not available - missing dependencies", {}
        
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
        if HAVE_TIKA:
            # Try with Tika first
            parsed = parser.from_file(file_path)
            text = parsed.get('content', '')
            metadata = parsed.get('metadata', {})
            
            # If Tika fails, use python-docx as fallback
            if not text and HAVE_DOCX:
                logger.info(f"Tika failed to extract text from {file_path}, using python-docx")
                doc = docx.Document(file_path)
                text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
                metadata = {"fallback_extraction": "python-docx"}
        elif HAVE_DOCX:
            # Use python-docx directly
            doc = docx.Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            metadata = {"extraction_method": "python-docx"}
        else:
            # No extraction methods available
            return f"Text extraction not available for {os.path.basename(file_path)}", {}
            
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
    if not HAVE_TESSERACT:
        return "OCR processing not available - pytesseract not installed", {}
        
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
    """Process an uploaded document to extract text and metadata"""
    try:
        print(f"Processing document: {document.title} (ID: {document.id})")
        document.processing_status = 'processing'
        document.save()

        # Get the file path
        file_path = document.file.path
        
        # Detect document type from extension
        _, extension = os.path.splitext(file_path)
        extension = extension.lower()
        
        # Set document type based on file extension
        if extension == '.pdf':
            document.document_type = 'pdf'
        elif extension in ['.docx', '.doc']:
            document.document_type = 'docx'
        elif extension == '.txt':
            document.document_type = 'txt'
        elif extension in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']:
            document.document_type = 'image'
        else:
            document.document_type = 'other'
        
        # Extract text using our enhanced function
        extracted_text = extract_text_from_document(file_path)
        
        # Update document with extracted text
        document.extracted_text = extracted_text
        document.processing_status = 'completed'
        document.save()
        
        print(f"Document processing completed: {len(extracted_text)} chars extracted")
        return True
        
    except Exception as e:
        print(f"Error processing document: {str(e)}")
        traceback.print_exc()
        
        # Update document with error
        document.processing_status = 'failed'
        document.error_message = str(e)
        document.save()
        
        return False 