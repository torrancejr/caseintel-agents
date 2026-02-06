"""
Script to seed the vector database with initial documents.
Run this after setting up the database to populate ChromaDB.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.rag.chunking import document_chunker
from src.rag.embeddings import vector_store
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_sample_documents():
    """
    Seed the vector database with sample documents for testing.
    """
    logger.info("Starting vector database seeding...")
    
    # Sample document 1: Contract
    sample_contract = """
    EMPLOYMENT AGREEMENT
    
    This Employment Agreement ("Agreement") is entered into as of January 15, 2024,
    between Acme Corporation ("Employer") and John Smith ("Employee").
    
    1. POSITION AND DUTIES
    Employee shall serve as Senior Software Engineer and shall perform duties
    as assigned by the Chief Technology Officer.
    
    2. COMPENSATION
    Employee shall receive an annual salary of $150,000, payable bi-weekly.
    
    3. TERM
    This Agreement shall commence on February 1, 2024 and continue for a period
    of two (2) years, unless terminated earlier as provided herein.
    
    4. CONFIDENTIALITY
    Employee agrees to maintain confidentiality of all proprietary information
    and trade secrets of Employer.
    
    5. NON-COMPETE
    For a period of 24 months following termination, Employee shall not engage
    in any business competitive with Employer within a 50-mile radius.
    
    6. GOVERNING LAW
    This Agreement shall be governed by the laws of the State of New York.
    
    IN WITNESS WHEREOF, the parties have executed this Agreement.
    
    Acme Corporation                    John Smith
    By: Jane Doe, CEO                   Employee
    Date: January 15, 2024              Date: January 15, 2024
    """
    
    # Sample document 2: Email
    sample_email = """
    From: jane.doe@acmecorp.com
    To: john.smith@acmecorp.com
    Date: March 10, 2024
    Subject: Re: Product Defect Issue
    
    John,
    
    I wanted to follow up on our conversation yesterday about the defect in
    the Widget 3000 product line. As we discussed, we became aware of the
    potential safety issue on February 15, 2024, but decided to continue
    shipping units while we investigated further.
    
    I know this is a sensitive matter, but I think we need to be transparent
    with our legal team about the timeline. Please make sure to document
    everything carefully.
    
    Best regards,
    Jane Doe
    CEO, Acme Corporation
    """
    
    # Chunk and add documents
    case_id = "sample_case_001"
    
    # Chunk contract
    logger.info("Chunking sample contract...")
    contract_chunks = document_chunker.chunk_document(
        text=sample_contract,
        document_type="contract",
        document_id="doc_contract_001",
        case_id=case_id
    )
    
    # Chunk email
    logger.info("Chunking sample email...")
    email_chunks = document_chunker.chunk_document(
        text=sample_email,
        document_type="email",
        document_id="doc_email_001",
        case_id=case_id
    )
    
    # Add to vector store
    logger.info("Adding chunks to vector store...")
    all_chunks = contract_chunks + email_chunks
    
    success = vector_store.add_document_chunks(
        case_id=case_id,
        chunks=all_chunks
    )
    
    if success:
        logger.info(f"Successfully seeded {len(all_chunks)} chunks for case {case_id}")
        logger.info("Vector database seeding complete!")
    else:
        logger.error("Failed to seed vector database")
        return False
    
    return True


def test_retrieval():
    """
    Test retrieval from the seeded vector database.
    """
    logger.info("\nTesting vector retrieval...")
    
    case_id = "sample_case_001"
    query = "What is the non-compete clause?"
    
    results = vector_store.search_similar_chunks(
        case_id=case_id,
        query_text=query,
        top_k=3
    )
    
    logger.info(f"\nQuery: {query}")
    logger.info(f"Found {len(results)} results:\n")
    
    for i, result in enumerate(results, 1):
        logger.info(f"Result {i}:")
        logger.info(f"  Document: {result['metadata'].get('document_id')}")
        logger.info(f"  Type: {result['metadata'].get('document_type')}")
        logger.info(f"  Text: {result['text'][:200]}...")
        logger.info("")


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("CaseIntel AI Agents - Vector Database Seeding")
    logger.info("=" * 60)
    
    # Seed documents
    if seed_sample_documents():
        # Test retrieval
        test_retrieval()
        logger.info("\n✅ Seeding and testing complete!")
    else:
        logger.error("\n❌ Seeding failed!")
        sys.exit(1)
