"""
Document retrieval and RAG (Retrieval-Augmented Generation) for Ask AI functionality.
"""
from src.rag.embeddings import vector_store
from src.agents.base import BaseAgent
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class RAGRetriever:
    """
    Retrieval-Augmented Generation system for document Q&A.
    """
    
    def __init__(self):
        """Initialize the RAG retriever."""
        self.vector_store = vector_store
        self.agent = BaseAgent(name="RAGRetriever")
    
    def find_related_documents(
        self,
        case_id: str,
        query_text: str,
        top_k: int = 5,
        exclude_doc_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find documents related to a query or document.
        Used by Agent 6 for cross-referencing.
        
        Args:
            case_id: Case identifier
            query_text: Query text or document summary
            top_k: Number of results
            exclude_doc_id: Optional document ID to exclude from results
            
        Returns:
            List of related document chunks
        """
        try:
            # Search vector store
            chunks = self.vector_store.search_similar_chunks(
                case_id=case_id,
                query_text=query_text,
                top_k=top_k * 2  # Get more, then filter
            )
            
            # Filter out excluded document
            if exclude_doc_id:
                chunks = [
                    c for c in chunks 
                    if c.get("metadata", {}).get("document_id") != exclude_doc_id
                ]
            
            # Limit to top_k
            chunks = chunks[:top_k]
            
            # Format for Agent 6
            related_docs = []
            seen_docs = set()
            
            for chunk in chunks:
                doc_id = chunk.get("metadata", {}).get("document_id")
                if doc_id and doc_id not in seen_docs:
                    seen_docs.add(doc_id)
                    related_docs.append({
                        "doc_id": doc_id,
                        "title": f"Document {doc_id}",
                        "summary": chunk.get("text", "")[:200] + "...",
                        "relevance": 1.0 - (chunk.get("distance", 0) / 2.0)  # Convert distance to relevance
                    })
            
            return related_docs
            
        except Exception as e:
            logger.error(f"Failed to find related documents: {str(e)}")
            return []
    
    def ask_question(
        self,
        case_id: str,
        question: str,
        top_k: int = 10
    ) -> Dict[str, Any]:
        """
        Answer a question about case documents using RAG.
        
        Args:
            case_id: Case identifier
            question: User's question
            top_k: Number of chunks to retrieve
            
        Returns:
            Dict with answer, sources, and confidence
        """
        try:
            logger.info(f"Answering question for case {case_id}: {question}")
            
            # Retrieve relevant chunks
            chunks = self.vector_store.search_similar_chunks(
                case_id=case_id,
                query_text=question,
                top_k=top_k
            )
            
            if not chunks:
                return {
                    "answer": "I couldn't find any relevant information in the case documents to answer this question.",
                    "sources": [],
                    "confidence": 0.0
                }
            
            # Build context from retrieved chunks
            context = "\n\n---\n\n".join([
                f"Document {c.get('metadata', {}).get('document_id', 'Unknown')} "
                f"(Page {c.get('metadata', {}).get('page', 'N/A')}):\n{c.get('text', '')}"
                for c in chunks
            ])
            
            # System prompt for Q&A
            system_prompt = """You are a legal AI assistant helping attorneys analyze case documents.

Your task is to answer questions about case documents based on the provided context.

Guidelines:
1. Answer based ONLY on the provided document excerpts
2. Cite specific documents and page numbers in your answer
3. If the context doesn't contain enough information, say so clearly
4. Be precise and factual - don't speculate or infer beyond what's stated
5. Use legal terminology appropriately
6. If there are contradictions in the documents, note them
7. Provide a confidence score (0.0-1.0) based on how well the context supports your answer

Format your response as a clear, well-structured answer with citations."""
            
            user_prompt = f"""Question: {question}

Relevant document excerpts:

{context}

Please answer the question based on these excerpts. Include specific citations to documents and pages."""
            
            # Get answer from Claude
            answer_text = self.agent._call_claude(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=4096
            )
            
            # Extract sources
            sources = []
            seen_docs = set()
            for chunk in chunks:
                doc_id = chunk.get("metadata", {}).get("document_id")
                if doc_id and doc_id not in seen_docs:
                    seen_docs.add(doc_id)
                    sources.append({
                        "document_id": doc_id,
                        "document_type": chunk.get("metadata", {}).get("document_type", "unknown"),
                        "page": chunk.get("metadata", {}).get("page"),
                        "excerpt": chunk.get("text", "")[:200] + "..."
                    })
            
            # Estimate confidence based on number and quality of sources
            confidence = min(1.0, len(chunks) / top_k * 0.8 + 0.2)
            
            logger.info(f"Generated answer with {len(sources)} sources (confidence: {confidence:.2f})")
            
            return {
                "answer": answer_text,
                "sources": sources,
                "confidence": confidence
            }
            
        except Exception as e:
            logger.error(f"Failed to answer question: {str(e)}")
            return {
                "answer": f"An error occurred while processing your question: {str(e)}",
                "sources": [],
                "confidence": 0.0
            }
    
    def get_document_summary(
        self,
        case_id: str,
        document_id: str
    ) -> Optional[str]:
        """
        Get a summary of a specific document from the vector store.
        
        Args:
            case_id: Case identifier
            document_id: Document identifier
            
        Returns:
            Document summary or None
        """
        try:
            # Search for chunks from this document
            chunks = self.vector_store.search_similar_chunks(
                case_id=case_id,
                query_text="summary overview",  # Generic query
                top_k=3,
                filter_metadata={"document_id": document_id}
            )
            
            if not chunks:
                return None
            
            # Combine first few chunks as summary
            summary = " ".join([c.get("text", "") for c in chunks[:2]])
            return summary[:500] + "..." if len(summary) > 500 else summary
            
        except Exception as e:
            logger.error(f"Failed to get document summary: {str(e)}")
            return None


# Singleton instance
rag_retriever = RAGRetriever()
