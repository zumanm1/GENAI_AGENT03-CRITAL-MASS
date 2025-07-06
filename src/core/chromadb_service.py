"""
ChromaDB Service
Vector database service for document storage and retrieval
"""

import logging
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

# Import configuration
from .config import config


class ChromaDBService:
    """ChromaDB service for vector database operations"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.client = None
        self.collection = None
        self.embedding_model = None
        self._initialize_chromadb()
        self._initialize_embedding_model()

    def _initialize_chromadb(self):
        """Initialize ChromaDB client and collection"""
        try:
            # Ensure persist directory exists
            persist_dir = config.chromadb['PERSIST_DIRECTORY']
            os.makedirs(persist_dir, exist_ok=True)

            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(
                path=persist_dir,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )

            # Get or create collection
            collection_name = config.chromadb['COLLECTION_NAME']
            try:
                self.collection = self.client.get_collection(
                    name=collection_name)
                self.logger.info(
                    f"Connected to existing ChromaDB collection: "
                    f"'{collection_name}'"
                )
            except Exception:
                self.collection = self.client.create_collection(
                    name=collection_name,
                    metadata={
                        "description":
                            "Network automation documents and configurations"
                    },
                )
                self.logger.info(
                    f"Created new ChromaDB collection: {collection_name}")

        except Exception as e:
            self.logger.error(f"Failed to initialize ChromaDB: {e}")
            raise

    def _initialize_embedding_model(self):
        """Initialize sentence transformer model for embeddings"""
        try:
            model_name = config.chromadb['EMBEDDING_MODEL']
            self.embedding_model = SentenceTransformer(model_name)
            self.logger.info(f"Loaded embedding model: {model_name}")
        except Exception as e:
            self.logger.error(f"Failed to load embedding model: {e}")
            raise

    def add_document(
        self, document_id: str, content: str, metadata: Dict[str, Any] = None
    ) -> bool:
        """Add a document to the vector database"""
        try:
            if metadata is None:
                metadata = {}

            # Add timestamp to metadata
            metadata['added_at'] = datetime.utcnow().isoformat()

            # Generate embedding
            embedding = self.embedding_model.encode(content).tolist()

            # Add to collection
            self.collection.add(
                documents=[content],
                embeddings=[embedding],
                metadatas=[metadata],
                ids=[document_id]
            )

            self.logger.info(f"Added document to ChromaDB: {document_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to add document {document_id}: {e}")
            return False

    def add_documents_batch(self, documents: List[Dict[str, Any]]) -> bool:
        """Add multiple documents in batch"""
        try:
            if not documents:
                return True

            ids = []
            contents = []
            embeddings = []
            metadatas = []

            for doc in documents:
                doc_id = doc['id']
                content = doc['content']
                metadata = doc.get('metadata', {})

                # Add timestamp to metadata
                metadata['added_at'] = datetime.utcnow().isoformat()

                # Generate embedding
                embedding = self.embedding_model.encode(content).tolist()

                ids.append(doc_id)
                contents.append(content)
                embeddings.append(embedding)
                metadatas.append(metadata)

            # Add batch to collection
            self.collection.add(
                documents=contents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )

            self.logger.info(f"Added {len(documents)} documents to ChromaDB")
            return True

        except Exception as e:
            self.logger.error(f"Failed to add documents batch: {e}")
            return False

    def search_documents(
        self, query: str, n_results: int = 5,
        filter_metadata: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()

            # Search in collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=filter_metadata,
                include=['documents', 'metadatas', 'distances']
            )

            # Format results
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    formatted_results.append({
                        'id': results['ids'][0][i],
                        'content': doc,
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i],
                        'similarity': 1 - results['distances'][0][i]
                    })

            self.logger.info(
                f"Found {len(formatted_results)} similar documents for query")
            return formatted_results

        except Exception as e:
            self.logger.error(f"Failed to search documents: {e}")
            return []

    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific document by ID"""
        try:
            results = self.collection.get(
                ids=[document_id],
                include=['documents', 'metadatas']
            )

            if results['documents'] and results['documents'][0]:
                return {
                    'id': document_id,
                    'content': results['documents'][0],
                    'metadata': results['metadatas'][0]
                }
            return None

        except Exception as e:
            self.logger.error(f"Failed to get document {document_id}: {e}")
            return None

    def delete_document(self, document_id: str) -> bool:
        """Delete a document from the vector database"""
        try:
            self.collection.delete(ids=[document_id])
            self.logger.info(f"Deleted document from ChromaDB: {document_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to delete document {document_id}: {e}")
            return False

    def update_document(
        self, document_id: str, content: str, metadata: Dict[str, Any] = None
    ) -> bool:
        """Update an existing document"""
        try:
            # Delete existing document
            self.delete_document(document_id)

            # Add updated document
            return self.add_document(document_id, content, metadata)

        except Exception as e:
            self.logger.error(f"Failed to update document {document_id}: {e}")
            return False

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        try:
            count = self.collection.count()
            return {
                'document_count': count,
                'collection_name': config.chromadb['COLLECTION_NAME'],
                'embedding_model': config.chromadb['EMBEDDING_MODEL'],
                'persist_directory': config.chromadb['PERSIST_DIRECTORY']
            }
        except Exception as e:
            self.logger.error(f"Failed to get collection stats: {e}")
            return {}

    def health_check(self) -> Dict[str, Any]:
        """Check ChromaDB service health"""
        try:
            stats = {
                'document_count': self.collection.count(),
                'collection_name': config.chromadb['COLLECTION_NAME'],
                'embedding_model': config.chromadb['EMBEDDING_MODEL']
            }

            return {
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'collection_stats': stats
            }

        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    def reset_collection(self) -> bool:
        """Reset (clear) the entire collection - USE WITH CAUTION"""
        try:
            collection_name = config.chromadb['COLLECTION_NAME']

            # Delete existing collection
            self.client.delete_collection(name=collection_name)

            # Create new collection
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={
                    "description": (
                        "Network automation documents and configurations"
                    )
                },
            )

            self.logger.warning(
                f"Reset ChromaDB collection: {collection_name}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to reset collection: {e}")
            return False


# Global ChromaDB service instance
chromadb_service = ChromaDBService()


# Dependency function
def get_chromadb_service() -> ChromaDBService:
    """Get ChromaDB service instance"""
    return chromadb_service
