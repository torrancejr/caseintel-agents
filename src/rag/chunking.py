"""
Document chunking strategies for legal documents.
Respects document structure and legal-specific patterns.
"""
import re
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class DocumentChunker:
    """
    Legal-document-aware chunking strategy.
    Respects document structure and doesn't split across important boundaries.
    """
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        respect_structure: bool = True
    ):
        """
        Initialize the chunker.
        
        Args:
            chunk_size: Target chunk size in tokens (approximate)
            chunk_overlap: Overlap between chunks in tokens
            respect_structure: Whether to respect document structure
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.respect_structure = respect_structure
    
    def chunk_document(
        self,
        text: str,
        document_type: str,
        document_id: str,
        case_id: str
    ) -> List[Dict[str, Any]]:
        """
        Chunk a document based on its type.
        
        Args:
            text: Document text
            document_type: Type of document (contract, email, deposition, etc.)
            document_id: Document identifier
            case_id: Case identifier
            
        Returns:
            List of chunk dictionaries with text and metadata
        """
        if document_type == "contract":
            return self._chunk_contract(text, document_id, case_id)
        elif document_type == "deposition":
            return self._chunk_deposition(text, document_id, case_id)
        elif document_type == "email":
            return self._chunk_email(text, document_id, case_id)
        else:
            return self._chunk_generic(text, document_id, case_id, document_type)
    
    def _chunk_contract(
        self,
        text: str,
        document_id: str,
        case_id: str
    ) -> List[Dict[str, Any]]:
        """
        Chunk a contract by clauses/sections.
        Preserves numbered sections and doesn't split mid-clause.
        """
        chunks = []
        
        # Split by section headers (e.g., "1.", "Section 1", "Article I")
        section_pattern = r'(?:^|\n)(?:Section|Article|SECTION|ARTICLE)?\s*[\dIVXivx]+\.?\s+[A-Z]'
        sections = re.split(section_pattern, text)
        
        current_chunk = ""
        current_section = None
        page_num = 1
        
        for i, section in enumerate(sections):
            if not section.strip():
                continue
            
            # Estimate tokens (rough: 1 token ≈ 4 characters)
            section_tokens = len(section) // 4
            current_tokens = len(current_chunk) // 4
            
            if current_tokens + section_tokens > self.chunk_size and current_chunk:
                # Save current chunk
                chunks.append({
                    "text": current_chunk.strip(),
                    "document_id": document_id,
                    "case_id": case_id,
                    "document_type": "contract",
                    "chunk_index": len(chunks),
                    "section": current_section,
                    "page": page_num
                })
                
                # Start new chunk with overlap
                overlap_text = current_chunk[-self.chunk_overlap * 4:] if self.chunk_overlap else ""
                current_chunk = overlap_text + section
            else:
                current_chunk += section
            
            current_section = f"Section {i}"
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append({
                "text": current_chunk.strip(),
                "document_id": document_id,
                "case_id": case_id,
                "document_type": "contract",
                "chunk_index": len(chunks),
                "section": current_section,
                "page": page_num
            })
        
        logger.info(f"Chunked contract into {len(chunks)} chunks")
        return chunks
    
    def _chunk_deposition(
        self,
        text: str,
        document_id: str,
        case_id: str
    ) -> List[Dict[str, Any]]:
        """
        Chunk a deposition by Q&A exchanges.
        Keeps question-answer pairs together.
        """
        chunks = []
        
        # Split by Q: or A: patterns
        qa_pattern = r'(?:^|\n)([QA]):\s*'
        parts = re.split(qa_pattern, text)
        
        current_chunk = ""
        current_qa_pair = ""
        page_num = 1
        
        for i in range(1, len(parts), 2):
            if i + 1 >= len(parts):
                break
            
            qa_type = parts[i]  # 'Q' or 'A'
            qa_text = parts[i + 1]
            
            qa_line = f"{qa_type}: {qa_text}"
            
            # Keep Q&A pairs together
            if qa_type == "Q":
                current_qa_pair = qa_line
            else:  # 'A'
                current_qa_pair += "\n" + qa_line
                
                # Check if we should create a chunk
                tokens = len(current_chunk + current_qa_pair) // 4
                if tokens > self.chunk_size and current_chunk:
                    chunks.append({
                        "text": current_chunk.strip(),
                        "document_id": document_id,
                        "case_id": case_id,
                        "document_type": "deposition",
                        "chunk_index": len(chunks),
                        "page": page_num
                    })
                    current_chunk = current_qa_pair
                else:
                    current_chunk += "\n" + current_qa_pair
                
                current_qa_pair = ""
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append({
                "text": current_chunk.strip(),
                "document_id": document_id,
                "case_id": case_id,
                "document_type": "deposition",
                "chunk_index": len(chunks),
                "page": page_num
            })
        
        logger.info(f"Chunked deposition into {len(chunks)} chunks")
        return chunks
    
    def _chunk_email(
        self,
        text: str,
        document_id: str,
        case_id: str
    ) -> List[Dict[str, Any]]:
        """
        Chunk an email thread.
        Keeps individual emails intact, doesn't split a single email.
        """
        chunks = []
        
        # Split by email headers (From:, To:, Subject:)
        email_pattern = r'(?:^|\n)(?:From|FROM):\s*'
        emails = re.split(email_pattern, text)
        
        for i, email in enumerate(emails):
            if not email.strip():
                continue
            
            # Each email is a chunk (unless extremely long)
            email_text = f"From: {email}" if i > 0 else email
            
            chunks.append({
                "text": email_text.strip(),
                "document_id": document_id,
                "case_id": case_id,
                "document_type": "email",
                "chunk_index": len(chunks),
                "email_index": i
            })
        
        logger.info(f"Chunked email thread into {len(chunks)} chunks")
        return chunks
    
    def _chunk_generic(
        self,
        text: str,
        document_id: str,
        case_id: str,
        document_type: str
    ) -> List[Dict[str, Any]]:
        """
        Generic chunking by paragraphs with overlap.
        """
        chunks = []
        
        # Split by paragraphs (double newline)
        paragraphs = text.split("\n\n")
        
        current_chunk = ""
        page_num = 1
        
        for para in paragraphs:
            if not para.strip():
                continue
            
            tokens = len(current_chunk + para) // 4
            
            if tokens > self.chunk_size and current_chunk:
                chunks.append({
                    "text": current_chunk.strip(),
                    "document_id": document_id,
                    "case_id": case_id,
                    "document_type": document_type,
                    "chunk_index": len(chunks),
                    "page": page_num
                })
                
                # Add overlap
                overlap_text = current_chunk[-self.chunk_overlap * 4:] if self.chunk_overlap else ""
                current_chunk = overlap_text + "\n\n" + para
            else:
                current_chunk += "\n\n" + para if current_chunk else para
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append({
                "text": current_chunk.strip(),
                "document_id": document_id,
                "case_id": case_id,
                "document_type": document_type,
                "chunk_index": len(chunks),
                "page": page_num
            })
        
        logger.info(f"Chunked document into {len(chunks)} chunks")
        return chunks


# Singleton instance
document_chunker = DocumentChunker()
