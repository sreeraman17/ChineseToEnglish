# translation_manager.py
from typing import List, Optional, Dict
import sqlite3
import logging
import hashlib
from dataclasses import asdict
from text_processor import TextChunk
import ollama
import time
import re
import json

logger = logging.getLogger(__name__)

class TranslationManager:
    def __init__(self, db_path: str = "translations.db"):
        """Initialize TranslationManager with enhanced features"""
        self.base_url = 'http://localhost:11434'
        self.db_path = db_path
        self.setup_database()
        
        # Comprehensive terminology database
        self.terminology = {
            "世界人权宣言": "Universal Declaration of Human Rights",
            "联合国": "United Nations",
            "大会": "General Assembly",
            "人权": "human rights",
            "基本自由": "fundamental freedoms",
            "会员国": "Member States",
            "序言": "Preamble",
            "鉴于": "Whereas",
            "条": "Article",
            "宣布": "Proclaims",
            "人的尊严": "human dignity",
            "人类家庭": "human family",
            "固有尊严": "inherent dignity",
            "不移的权利": "inalienable rights",
            "法治": "rule of law",
            "正义": "justice",
            "和平": "peace",
            "自由": "freedom",
            "人格尊严": "dignity of the human person",
            "平等权利": "equal rights",
            "社会进步": "social progress",
            "生活水平": "standard of life",
            "普遍性": "universality",
            "不可分割性": "indivisibility",
            "相互依存性": "interdependence",
            "民主社会": "democratic society",
        }

    def setup_database(self):
        """Initialize SQLite database with enhanced caching"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS translations (
                        chunk_hash TEXT PRIMARY KEY,
                        original_text TEXT,
                        translated_text TEXT,
                        document_type TEXT,
                        quality_score FLOAT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                logger.debug(f"Database initialized at {self.db_path}")
        except Exception as e:
            logger.error(f"Database initialization failed: {str(e)}")
            raise Exception(f"Failed to setup database: {str(e)}")

    def _generate_chunk_hash(self, text: str) -> str:
        """Generate a consistent hash for a text chunk"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    def get_cached_translation(self, chunk: TextChunk) -> Optional[str]:
        """Check if translation exists in cache"""
        try:
            chunk_hash = self._generate_chunk_hash(chunk.content)
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                result = cursor.execute(
                    "SELECT translated_text FROM translations WHERE chunk_hash = ?",
                    (chunk_hash,)
                ).fetchone()
                
                if result and result[0].strip():
                    logger.debug(f"Cache hit for chunk {chunk.id}")
                    return result[0]
                logger.debug(f"Cache miss for chunk {chunk.id}")
                return None
        except Exception as e:
            logger.error(f"Cache retrieval error: {str(e)}")
            return None

    def cache_translation(self, chunk: TextChunk, translation: str, document_type: str = "general"):
        """Store translation in cache"""
        try:
            chunk_hash = self._generate_chunk_hash(chunk.content)
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """INSERT OR REPLACE INTO translations 
                    (chunk_hash, original_text, translated_text, document_type) 
                    VALUES (?, ?, ?, ?)""",
                    (chunk_hash, chunk.content, translation, document_type)
                )
                logger.debug(f"Cached translation for chunk {chunk.id}")
        except Exception as e:
            logger.error(f"Failed to cache translation: {str(e)}")

    def apply_terminology(self, translation: str) -> str:
        """Apply consistent terminology with context awareness"""
        for cn_term, en_term in self.terminology.items():
            translation = re.sub(fr'\b{cn_term}\b', en_term, translation)
        return translation

    def validate_translation(self, original: str, translation: str) -> bool:
        """Comprehensive translation validation with enhanced character checks"""
        if not translation.strip():
            logger.error("Empty translation detected")
            return False
        
        # Check for untranslated Chinese characters with detailed logging
        chinese_chars = re.findall(r'[\u4e00-\u9fff]', translation)
        if chinese_chars:
            logger.error(f"Found untranslated Chinese characters: {chinese_chars}")
            return False
        
        # Check for incomplete translations (bracketed terms)
        if re.search(r'\([^)]*[\u4e00-\u9fff][^)]*\)', translation):
            logger.error("Found bracketed Chinese characters")
            return False
        
        # Detect mixed language patterns
        mixed_patterns = [
            r'[\u4e00-\u9fff][a-zA-Z]',  # Chinese followed by English
            r'[a-zA-Z][\u4e00-\u9fff]',  # English followed by Chinese
        ]
        for pattern in mixed_patterns:
            if re.search(pattern, translation):
                logger.error("Found mixed language patterns")
                return False
        
        # Validate parenthetical translations
        parenthetical_pattern = r'\(([^)]+)\)'
        parentheticals = re.findall(parenthetical_pattern, translation)
        for p in parentheticals:
            if re.search(r'[\u4e00-\u9fff]', p):
                logger.error("Found Chinese characters in parenthetical expressions")
                return False
        
        return True

    def post_process_translation(self, translation: str, doc_type: str = "general") -> str:
        """Enhanced post-processing with better character handling"""
        # Remove any remaining Chinese characters and their surrounding brackets/parentheses
        translation = re.sub(r'\s*\([^)]*[\u4e00-\u9fff][^)]*\)\s*', '', translation)
        translation = re.sub(r'\s*\[[^\]]*[\u4e00-\u9fff][^\]]*\]\s*', '', translation)
        
        # Clean up spaces around punctuation
        translation = re.sub(r'\s+([,.!?;:])', r'\1', translation)
        
        # Normalize whitespace
        translation = re.sub(r'\s+', ' ', translation)
        translation = translation.strip()
        
        # Remove any remaining bracketed terms that might be translation artifacts
        translation = re.sub(r'\s*\(.*?\)\s*', ' ', translation)
        translation = re.sub(r'\s+', ' ', translation)
        
        return translation.strip()

    def translate_chunk(self, chunk: TextChunk, context: Optional[Dict] = None) -> str:
        """Enhanced translation with better error handling and validation"""
        try:
            cached = self.get_cached_translation(chunk)
            if cached:
                return cached

            # Enhanced prompt with explicit character translation requirements
            prompt = f"""Translate this Chinese text to English:

SOURCE TEXT:
{chunk.content}

CRITICAL REQUIREMENTS:
1. Translate ALL Chinese characters - no untranslated characters allowed
2. Do not include original Chinese characters in brackets or parentheses
3. Provide complete English translations for all terms
4. Use natural English phrasing
5. Maintain the original meaning accurately

Translation:"""
            
            # First pass - basic translation
            response = ollama.chat(model='qwen2.5:7b', messages=[
                {
                    'role': 'system',
                    'content': 'You are a professional translator. Translate everything to English completely.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ])
            
            initial_translation = response['message']['content'].strip()
            
            # Second pass - verification and refinement
            refine_prompt = f"""Review and improve this translation:

Original Chinese: {chunk.content}
Current translation: {initial_translation}

REQUIREMENTS:
1. Ensure ALL Chinese characters are translated to English
2. Remove any remaining Chinese characters
3. Use clear English equivalents for all terms
4. Maintain natural English flow
5. Keep the original meaning

Improved translation:"""
            
            response = ollama.chat(model='qwen2.5:7b', messages=[
                {
                    'role': 'system',
                    'content': 'You are a translation reviewer. Ensure complete English translation with no Chinese characters.'
                },
                {
                    'role': 'user',
                    'content': refine_prompt
                }
            ])
            
            refined_translation = response['message']['content'].strip()
            
            # Apply terminology and post-processing
            translated = self.apply_terminology(refined_translation)
            final_translation = self.post_process_translation(translated)
            
            if not self.validate_translation(chunk.content, final_translation):
                raise Exception("Translation validation failed - found untranslated content")
            
            self.cache_translation(chunk, final_translation)
            
            return final_translation
            
        except Exception as e:
            logger.error(f"Translation error for chunk {chunk.id}: {str(e)}")
            raise Exception(f"Translation failed: {str(e)}")

    def translate_chunks(self, chunks: List[TextChunk], progress_callback=None) -> List[TextChunk]:
        """Translate all chunks with progress tracking and error handling"""
        if not chunks:
            return []
            
        total_chunks = len(chunks)
        translated_chunks = []
        
        for i, chunk in enumerate(chunks):
            try:
                if not chunk.content.strip():
                    logger.warning(f"Skipping empty chunk {chunk.id}")
                    continue
                    
                translation = self.translate_chunk(chunk)
                chunk.translation = translation
                chunk.is_translated = True
                translated_chunks.append(chunk)
                
                if progress_callback:
                    progress = (i + 1) / total_chunks * 100
                    progress_callback(progress)
                
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                logger.error(f"Failed to translate chunk {chunk.id}: {str(e)}")
                chunk.translation = f"[Translation Error: {str(e)}]"
                translated_chunks.append(chunk)
                
        return translated_chunks

    def reassemble_document(self, chunks: List[TextChunk]) -> dict:
        """Reassemble translated chunks into complete document"""
        try:
            if not chunks:
                raise ValueError("No chunks provided for reassembly")
            
            # Sort chunks by sequence number
            chunks.sort(key=lambda x: x.sequence_number)
            
            # Validate translations
            for chunk in chunks:
                if not chunk.is_translated or not chunk.translation.strip():
                    logger.warning(f"Chunk {chunk.id} has invalid translation")
            
            original_text = "\n".join(chunk.content for chunk in chunks)
            translated_text = "\n".join(chunk.translation for chunk in chunks if chunk.is_translated)
            
            # Final validation
            if not translated_text.strip():
                raise ValueError("No valid translations in reassembled document")
            
            return {
                "original": original_text,
                "translated": translated_text,
                "chunks": [asdict(chunk) for chunk in chunks],
                "metadata": {
                    "total_chunks": len(chunks),
                    "successful_translations": sum(1 for c in chunks if c.is_translated)
                }
            }
        except Exception as e:
            logger.error(f"Document reassembly failed: {str(e)}")
            raise Exception(f"Failed to reassemble document: {str(e)}")