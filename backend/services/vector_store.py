import chromadb
from chromadb.config import Settings
import google.generativeai as genai
from typing import List, Dict, Any

from backend.core.config import settings
from backend.core.logger import logger

genai.configure(api_key=settings.GEMINI_API_KEY)

class VectorStore:
    """
    Persistent Vector Store Service using ChromaDB.
    Uses Google Gemini as the embedding model.
    """
    def __init__(self):
        # Initialize persistent local storage for ChromaDB
        self.client = chromadb.PersistentClient(path="./data/chromadb")
        self.collection_name = "bizrithm_knowledge_base"
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        logger.info(f"Initialized ChromaDB vector store collection: {self.collection_name}")

    def _get_embedding(self, text: str) -> List[float]:
        """Generate embedding using Gemini API."""
        try:
            result = genai.embed_content(
                model="models/embedding-001",
                content=text,
                task_type="retrieval_document",
            )
            return result['embedding']
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            # Fallback zero-vector if rate limited
            return [0.0] * 768

    def add_document(self, doc_id: str, text: str, metadata: Dict[str, Any] = None):
        """Embed and add a document to the vector store."""
        embedding = self._get_embedding(text)
        
        self.collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[metadata or {}]
        )
        logger.info(f"Added document {doc_id} to vector store.")

    def add_documents(self, doc_ids: List[str], texts: List[str], metadatas: List[Dict[str, Any]] = None):
        """Embed and add multiple documents."""
        embeddings = [self._get_embedding(text) for text in texts]
        self.collection.add(
            ids=doc_ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas or [{}] * len(texts)
        )
        logger.info(f"Added {len(texts)} documents to vector store.")

    def query_similar(self, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """Find most similar documents to the query."""
        if self.collection.count() == 0:
            return []
            
        try:
            query_embedding = self._get_embedding(query)
            
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=min(n_results, self.collection.count())
            )
            
            formatted_results = []
            if results['documents'] and len(results['documents']) > 0:
                for i in range(len(results['documents'][0])):
                    formatted_results.append({
                        "id": results['ids'][0][i],
                        "document": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                        "distance": results['distances'][0][i] if results['distances'] else 0.0
                    })
            return formatted_results
        except Exception as e:
            logger.error(f"Error querying vector store: {e}")
            return []

    def clear_database(self):
        """Clear all stored vectors."""
        try:
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.create_collection(self.collection_name)
            logger.info("Cleared vector store.")
        except Exception as e:
            logger.error(f"Error clearing vector store: {e}")


# Singleton instance
_vector_store_instance = None

def get_vector_store() -> VectorStore:
    global _vector_store_instance
    if _vector_store_instance is None:
        _vector_store_instance = VectorStore()
    return _vector_store_instance
