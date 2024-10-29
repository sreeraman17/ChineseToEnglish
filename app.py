from flask import Flask, render_template, request, jsonify, Response
import tempfile
import os
import logging
from text_processor import TextProcessor
from translation_manager import TranslationManager
import json
from werkzeug.utils import secure_filename
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configure maximum file upload size (16MB)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Ensure the uploads directory exists
UPLOAD_FOLDER = Path('uploads')
UPLOAD_FOLDER.mkdir(exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize processors
text_processor = TextProcessor(chunk_size=500)
translation_manager = TranslationManager()

def allowed_file(filename):
    """Check if the file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and translation"""
    logger.debug("Upload endpoint hit")
    
    # Validate file presence
    if 'file' not in request.files:
        logger.error("No file part in request")
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    # Validate filename
    if file.filename == '':
        logger.error("No file selected")
        return jsonify({'error': 'No file selected'}), 400
    
    # Validate file type
    if not allowed_file(file.filename):
        logger.error("Invalid file type")
        return jsonify({'error': 'Please upload a PDF file'}), 400
    
    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        logger.debug(f"Processing file: {filename}")
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            logger.debug(f"Created temp file: {temp_file.name}")
            file.save(temp_file.name)
            
            # Extract text from PDF
            try:
                logger.debug("Extracting text from PDF")
                extracted_text = text_processor.extract_from_pdf(temp_file.name)
                logger.debug(f"Extracted text length: {len(extracted_text)}")
                
                if not extracted_text.strip():
                    raise ValueError("No text could be extracted from the PDF")
                
            except Exception as e:
                logger.error(f"Text extraction failed: {str(e)}")
                return jsonify({'error': f'Failed to extract text from PDF: {str(e)}'}), 400
            
            # Clean and validate text
            try:
                cleaned_text = text_processor.clean_text(extracted_text)
                logger.debug(f"Cleaned text length: {len(cleaned_text)}")
                
                if not cleaned_text.strip():
                    raise ValueError("Text was empty after cleaning")
                
                # Verify it's Chinese
                if not text_processor.is_chinese(cleaned_text):
                    logger.error("Text is not Chinese")
                    return jsonify({
                        'error': 'The uploaded file does not appear to contain Chinese text',
                        'details': 'Please ensure the PDF contains Chinese text'
                    }), 400
                
            except Exception as e:
                logger.error(f"Text cleaning/validation failed: {str(e)}")
                return jsonify({'error': f'Failed to process text: {str(e)}'}), 400
            
            # Create text chunks
            try:
                logger.debug("Creating text chunks")
                chunks = text_processor.create_chunks(cleaned_text)
                
                if not chunks:
                    logger.error("No chunks created from text")
                    return jsonify({
                        'error': 'Could not process the text into chunks',
                        'details': 'The text might be too short or empty'
                    }), 400
                
                logger.debug(f"Created {len(chunks)} chunks")
                
            except Exception as e:
                logger.error(f"Chunking failed: {str(e)}")
                return jsonify({'error': f'Failed to process text into chunks: {str(e)}'}), 500
            
            # Translate chunks
            try:
                logger.debug("Starting translation")
                translated_chunks = translation_manager.translate_chunks(chunks)
                
                if not translated_chunks:
                    raise ValueError("No translations were produced")
                
                logger.debug("Translation completed")
                
            except Exception as e:
                logger.error(f"Translation failed: {str(e)}")
                return jsonify({'error': f'Translation failed: {str(e)}'}), 500
            
            # Reassemble document
            try:
                logger.debug("Reassembling document")
                result = translation_manager.reassemble_document(translated_chunks)
                
                if not result or not result.get('translated'):
                    raise ValueError("Failed to reassemble translated document")
                
                logger.debug("Processing completed successfully")
                return jsonify(result)
                
            except Exception as e:
                logger.error(f"Document reassembly failed: {str(e)}")
                return jsonify({'error': f'Failed to reassemble translated document: {str(e)}'}), 500
            
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}", exc_info=True)
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500
        
    finally:
        # Clean up temporary file
        if 'temp_file' in locals():
            try:
                logger.debug(f"Cleaning up temp file: {temp_file.name}")
                os.unlink(temp_file.name)
            except Exception as e:
                logger.error(f"Failed to clean up temporary file: {str(e)}")

@app.route('/status')
def system_status():
    """Check system readiness"""
    try:
        # Check if translation service is available
        import ollama
        response = ollama.list()
        logger.debug("System status check: OK")
        return jsonify({
            'status': 'ready',
            'details': {
                'translation_service': 'online',
                'models_available': True
            }
        })
    except Exception as e:
        logger.error(f"System status check failed: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'details': {
                'translation_service': 'offline'
            }
        }), 503

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error"""
    logger.error("File too large error")
    return jsonify({
        'error': 'File too large',
        'details': 'Maximum file size is 16MB'
    }), 413

@app.errorhandler(500)
def internal_server_error(error):
    """Handle internal server errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        'error': 'Internal server error',
        'details': 'An unexpected error occurred'
    }), 500

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    logger.error(f"Not found error: {str(error)}")
    return jsonify({
        'error': 'Not found',
        'details': 'The requested resource was not found'
    }), 404

if __name__ == '__main__':
    logger.info("Starting application...")
    app.run(debug=True, port=5000)