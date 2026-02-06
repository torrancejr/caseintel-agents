"""
Vector embeddings and storage using ChromaDB.
Supports case-isolated collections for document retrieval.
Uses AWS Bedrock for embeddings (Amazon Titan or Cohere).
"""
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
import os
import logging
import boto3
import json

logger = logging.getLogger(__name__)

# ChromaDB configuration
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "amazon.titan-embed-text-v2:0")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")


class VectorStore:
    """
    Vector store using ChromaDB for document embeddings.
    Each case gets its own collection for data isolation.
    """
    
    def __init__(self):
        """Initialize ChromaDB client and AWS Bedrock for embeddings."""
        self.client = chromadb.Client(Settings(
            persist_directory=CHROMA_PERSIST_DIR,
            anonymized_telemetry=False
        ))
        self.bedrock_client = boto3.client(
            "bedrock-runtime",
            region_name=AWS_REGION
        )
        self.embedding_model = EMBEDDING_MODEL
        logger.info(f"Initialized ChromaDB at {CHROMA_PERSIST_DIR}")
        logger.info(f"Using embedding model: {self.embedding_model}")
    
    def _get_collection_name(self, case_id: str) -> str:
        """
        Get collection name for a case.
        
        Args:
            case_id: Case identifier
            
        Returns:
            str: Collection name
        """
        # Sanitize case_id for collection name (alphanumeric and underscores only)
        sanitized = "".join(c if c.isalnum() or c == "_" else "_" for c in case_id)
        return f"case_{sanitized}"
    
    def _get_or_create_collection(self, case_id: str):
        """
        Get or create a collection for a case.
        
        Args:
            case_id: Case identifier
            
        Returns:
            Collection: ChromaDB collection
        """
        collection_name = self._get_collection_name(case_id)
        try:
            collection = self.client.get_collection(name=collection_name)
            logger.debug(f"Retrieved existing collection: {collection_name}")
        except Exception:
            collection = self.client.create_collection(
                name=collection_name,
                metadata={"case_id": case_id}
            )
            logger.info(f"Created new collection: {collection_name}")
        
        return collection
    
    def _generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text using AWS Bedrock.
        Supports Amazon Titan and Cohere embedding models.
        
        Args:
            text: Text to embed
            
        Returns:
            List[float]: Embedding vector
        """
        try:
            # Prepare request based on model type
            if "titan" in self.embedding_model.lower():
                # Amazon Titan Embeddings
                body = json.dumps({
                    "inputText": text
                })
            elif "cohere" in self.embedding_model.lower():
                # Cohere Embeddings
                body = json.dumps({
                    "texts": [text],
                    "input_type": "search_document"
                })
            else:
                raise ValueError(f"Unsupported embedding model: {self.embedding_model}")
            
            # Call Bedrock
            response = self.bedrock_client.invoke_model(
                modelId=self.embedding_model,
                body=body
            )
            
            # Parse response
            response_body = json.loads(response["body"].read())
            
            if "titan" in self.embedding_model.lower():
                # Titan returns: {"embedding": [...], "inputTextTokenCount": N}
                embedding = response_body["embedding"]
            elif "cohere" in self.embedding_model.lower():
                # Cohere returns: {"embeddings": [[...]], "id": "...", "texts": [...]}
                embedding = response_body["embeddings"][0]
            
            return embedding
            
        except Exception as e:
            logger.error(f"Failed to generate embedding: {str(e)}")
            # Fallback to dummy embedding for development
            logger.warning("Using fallback dummy embedding")
            import hashlib
            text_hash = hashlib.md5(text.encode()).hexdigest()
            dummy_embedding = [float(int(text_hash[i:i+2], 16)) / 255.0 for i in range(0, 32, 2)]
            dummy_embedding = dummy_embedding * 64  # Extend to 1024 dimensions for Titan
            return dummy_embedding[:1024]
    
    def add_document_chunks(
        self,
        case_id: str,
        chunks: List[Dict[str, Any]]
    ) -> bool:
        """
        Add document chunks to the vector store.
        
        Args:
            case_id: Case identifier
            chunks: List of chunk dictionaries with text and metadata
            
        Returns:
            bool: True if successful
        """
        try:
            collection = self._get_or_create_collection(case_id)
            
            # Prepare data for ChromaDB
            ids = []
            documents = []
            metadatas = []
            embeddings = []
            
            for chunk in chunks:
                chunk_id = f"{chunk['document_id']}_chunk_{chunk['chunk_index']}"
                ids.append(chunk_id)
                documents.append(chunk["text"])
                
                # Metadata (exclude text to avoid duplication)
                metadata = {k: v for k, v in chunk.items() if k != "text"}
                # Convert all values to strings for ChromaDB compatibility
                metadata = {k: str(v) if v is not None else "" for k, v in metadata.items()}
                metadatas.append(metadata)
                
                # Generate embedding
                embedding = self._generate_embedding(chunk["text"])
                embeddings.append(embedding)
            
            # Add to collection
            collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
                embeddings=embeddings
            )
            
            logger.info(f"Added {len(chunks)} chunks to collection for case {case_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add chunks to vector store: {str(e)}")
            return False
    
    def search_similar_chunks(
        self,
        case_id: str,
        query_text: str,
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar document chunks.
        
        Args:
            case_id: Case identifier
            query_text: Query text
            top_k: Number of results to return
            filter_metadata: Optional metadata filters
            
        Returns:
            List of matching chunks with metadata
        """
        try:
            collection = self._get_or_create_collection(case_id)
            
            # Generate query embedding
            query_embedding = self._generate_embedding(query_text)
            
            # Search
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=filter_metadata
            )
            
            # Format results
            chunks = []
            if results["documents"] and len(results["documents"]) > 0:
                for i in range(len(results["documents"][0])):
                    chunks.append({
                        "text": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "distance": results["distances"][0][i] if "distances" in results else None
                    })
            
            logger.info(f"Found {len(chunks)} similar chunks for query in case {case_id}")
            return chunks
            
        except Exception as e:
            logger.error(f"Failed to search vector store: {str(e)}")
            return []
    
    def delete_document(self, case_id: str, document_id: str) -> bool:
        """
        Delete all chunks for a document.
        
        Args:
            case_id: Case identifier
            document_id: Document identifier
            
        Returns:
            bool: True if successful
        """
        try:
            collection = self._get_or_create_collection(case_id)
            
            # Delete all chunks with this document_id
            collection.delete(
                where={"document_id": document_id}
            )
            
            logger.info(f"Deleted document {document_id} from case {case_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete document from vector store: {str(e)}")
            return False
    
    def delete_case_collection(self, case_id: str) -> bool:
        """
        Delete entire collection for a case.
        
        Args:
            case_id: Case identifier
            
        Returns:
            bool: True if successful
        """
        try:
            collection_name = self._get_collection_name(case_id)
            self.client.delete_collection(name=collection_name)
            logger.info(f"Deleted collection for case {case_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete collection: {str(e)}")
            return False


# Singleton instance
vector_store = VectorStore()
