"""
Simple Document Processor
Basic document ingestion for demo purposes
"""

from src.core.database import db_manager
from src.core.chromadb_service import chromadb_service
import os
import logging
from typing import Dict, Any
import PyPDF2
import uuid
from datetime import datetime

# Import services
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(
    os.path.dirname(__file__), '..', '..', 'config'))


class DocumentProcessor:
    """Simple document processor for demo"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def process_text_file(
        self, file_path: str, metadata: Dict[str, Any] = None
    ) -> bool:
        """Process a text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            filename = os.path.basename(file_path)
            doc_id = str(uuid.uuid4())

            if metadata is None:
                metadata = {}

            metadata.update({
                'filename': filename,
                'file_type': 'text',
                'processed_at': datetime.utcnow().isoformat()
            })

            # Add to ChromaDB
            success = chromadb_service.add_document(doc_id, content, metadata)

            if success:
                # Save to database
                db_manager.create_document({
                    'filename': filename,
                    'original_filename': filename,
                    'file_type': 'text',
                    'file_size': len(content),
                    'file_path': file_path,
                    'status': 'processed',
                    'extracted_text': content[:1000],  # First 1000 chars
                    'chunk_count': 1,
                    'vector_ids': doc_id
                })

                self.logger.info(f"Processed text file: {filename}")
                return True

            return False

        except Exception as e:
            self.logger.error(f"Error processing text file {file_path}: {e}")
            return False

    def process_pdf_file(
        self, file_path: str, metadata: Dict[str, Any] = None
    ) -> bool:
        """Process a PDF file"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                content = ""

                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    content += page.extract_text() + "\n"

            filename = os.path.basename(file_path)
            doc_id = str(uuid.uuid4())

            if metadata is None:
                metadata = {}

            metadata.update({
                'filename': filename,
                'file_type': 'pdf',
                'pages': len(pdf_reader.pages),
                'processed_at': datetime.utcnow().isoformat()
            })

            # Add to ChromaDB
            success = chromadb_service.add_document(doc_id, content, metadata)

            if success:
                # Save to database
                db_manager.create_document({
                    'filename': filename,
                    'original_filename': filename,
                    'file_type': 'pdf',
                    'file_size': os.path.getsize(file_path),
                    'file_path': file_path,
                    'status': 'processed',
                    'extracted_text': content[:1000],  # First 1000 chars
                    'chunk_count': 1,
                    'vector_ids': doc_id
                })

                self.logger.info(f"Processed PDF file: {filename}")
                return True

            return False

        except Exception as e:
            self.logger.error(f"Error processing PDF file {file_path}: {e}")
            return False

    def process_file(
        self, file_path: str, metadata: Dict[str, Any] = None
    ) -> bool:
        """Process any supported file type"""
        if not os.path.exists(file_path):
            self.logger.error(f"File not found: {file_path}")
            return False

        file_ext = os.path.splitext(file_path)[1].lower()

        if file_ext == '.pdf':
            return self.process_pdf_file(file_path, metadata)
        elif file_ext in ['.txt', '.md']:
            return self.process_text_file(file_path, metadata)
        else:
            self.logger.error(f"Unsupported file type: {file_ext}")
            return False


# Global processor instance
document_processor = DocumentProcessor()
