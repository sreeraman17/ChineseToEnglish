# text_processor.py
import pdfplumber
import re
from typing import List
import langdetect
from dataclasses import dataclass
import logging
from langdetect.lang_detect_exception import LangDetectException

logger = logging.getLogger(__name__)

@dataclass
class TextChunk:
    id: int
    content: str
    is_translated: bool = False
    translation: str = ""
    sequence_number: int = 0

class TextProcessor:
    def __init__(self, chunk_size: int = 500):
        self.chunk_size = chunk_size

    def extract_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF while preserving structure"""
        full_text = ""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        logger.debug(f"Extracted text from page: {text[:100]}...")
                        full_text += text + "\n"
            
            if not full_text.strip():
                raise Exception("No text could be extracted from the PDF")
                
            return full_text.strip()
        except Exception as e:
            raise Exception(f"PDF extraction failed: {str(e)}")

    def clean_text(self, text: str) -> str:
        """Clean and normalize text with improved Chinese text handling"""
        logger.debug(f"Original text before cleaning: {text}")
        
        # Remove extra spaces between Chinese characters while preserving structure
        text = re.sub(r'(?<=[\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff])', '', text)
        
        # Preserve newlines for structure
        text = text.replace('\n', ' NEW_LINE ')
        
        # Remove excessive whitespace but keep single spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Restore newlines
        text = text.replace(' NEW_LINE ', '\n')
        
        # Clean up any remaining unnecessary characters while preserving Chinese text and punctuation
        text = re.sub(r'[^\u4e00-\u9fff.,!?;:\s\n。！？；：、，]', '', text)
        
        # Final cleanup of any double spaces or empty lines
        text = re.sub(r'\n\s*\n', '\n', text)
        text = re.sub(r' +', ' ', text)
        
        cleaned = text.strip()
        logger.debug(f"Cleaned text: {cleaned}")
        return cleaned

    def is_chinese(self, text: str) -> bool:
        """Verify if text is primarily Chinese using improved detection"""
        if not text.strip():
            logger.error("Empty text provided for Chinese detection")
            return False
            
        try:
            # Count Chinese characters (improved to handle punctuation)
            chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
            # Count meaningful characters (excluding whitespace and basic punctuation)
            meaningful_chars = re.sub(r'[\s.,!?;:\n]', '', text)
            total_chars = len(meaningful_chars) if meaningful_chars else 0
            
            chinese_ratio = len(chinese_chars) / total_chars if total_chars > 0 else 0
            
            logger.debug(f"Chinese characters: {len(chinese_chars)}")
            logger.debug(f"Total meaningful characters: {total_chars}")
            logger.debug(f"Chinese ratio: {chinese_ratio}")
            
            # Try langdetect with error handling
            try:
                # Use more text for detection
                sample_text = text[:1000].replace('\n', ' ')
                detected = langdetect.detect(sample_text)
                logger.debug(f"Language detected: {detected}")
                is_chinese_by_detect = detected in ['zh-cn', 'zh-tw', 'zh']
            except LangDetectException:
                logger.warning("Language detection failed, falling back to ratio")
                is_chinese_by_detect = False
            
            # Lower threshold for Chinese ratio since we're counting meaningful chars only
            is_chinese_by_ratio = chinese_ratio > 0.3
            
            logger.debug(f"Detection results - langdetect: {is_chinese_by_detect}, ratio: {is_chinese_by_ratio}")
            
            return is_chinese_by_detect or is_chinese_by_ratio
            
        except Exception as e:
            logger.error(f"Chinese detection error: {e}")
            return False
    
    def create_chunks(self, text: str) -> List[TextChunk]:
        """Split text into manageable chunks while preserving Chinese sentence structure"""
        if not text.strip():
            logger.warning("Empty text provided for chunking")
            return []
            
        chunks = []
        chunk_id = 0
        current_chunk = ""
        
        # Split by newlines first to preserve structure
        paragraphs = text.split('\n')
        
        for paragraph in paragraphs:
            if not paragraph.strip():
                continue
            
            # Split at Chinese and English sentence boundaries
            sentences = re.split(r'([。！？.!?])', paragraph)
            
            for i in range(0, len(sentences), 2):
                sentence = sentences[i] + (sentences[i+1] if i+1 < len(sentences) else '')
                
                if not sentence.strip():
                    continue
                
                if len(current_chunk) + len(sentence) > self.chunk_size:
                    if current_chunk:
                        chunks.append(TextChunk(
                            id=chunk_id,
                            content=current_chunk.strip(),
                            sequence_number=len(chunks)
                        ))
                        chunk_id += 1
                        current_chunk = sentence
                else:
                    current_chunk += sentence
            
            if current_chunk and not current_chunk.endswith('\n'):
                current_chunk += '\n'
        
        # Add the last chunk if there's anything left
        if current_chunk.strip():
            chunks.append(TextChunk(
                id=chunk_id,
                content=current_chunk.strip(),
                sequence_number=len(chunks)
            ))
        
        logger.debug(f"Created {len(chunks)} chunks")
        for chunk in chunks:
            logger.debug(f"Chunk {chunk.id}: {chunk.content[:50]}...")
        
        return chunks