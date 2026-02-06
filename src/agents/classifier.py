"""
Agent 1: Document Classifier
Identifies the type of legal document uploaded.
"""
from src.agents.base import BaseAgent
from src.workflows.state import DocumentType
import logging
import os

logger = logging.getLogger(__name__)

# System prompt for document classification
CLASSIFIER_SYSTEM_PROMPT = """You are an expert legal document classifier with deep knowledge of legal document types and structures.

Your task is to analyze legal documents and classify them into one of these categories:
- email: Email correspondence
- contract: Contracts, agreements, terms of service
- deposition: Deposition transcripts, testimony
- pleading: Complaints, motions, briefs, legal filings
- medical_record: Medical records, health documents
- correspondence: Letters, memos, non-email correspondence
- financial: Financial statements, invoices, receipts
- discovery_response: Interrogatory responses, document production responses
- exhibit: Exhibits attached to filings
- other: Documents that don't fit other categories

Classification Guidelines:
1. Analyze document structure, formatting, headers, and content patterns
2. Look for legal-specific markers:
   - Bates numbers (e.g., "ACME_00001234")
   - Case captions (e.g., "Smith v. Jones, Case No. 2024-CV-1234")
   - Signature blocks with attorney information
   - Header/footer patterns typical of legal documents
   - Court filing stamps or docket numbers
3. Consider content patterns:
   - Contracts: parties, recitals, numbered clauses, signature blocks, "WHEREAS" clauses
   - Depositions: Q&A format, court reporter certification, "EXAMINATION BY"
   - Pleadings: "COMES NOW", numbered paragraphs, "WHEREFORE", prayer for relief
   - Emails: From/To/Subject headers, email threading indicators
4. Return a confidence score (0.0-1.0):
   - 0.9-1.0: Very confident, clear document type
   - 0.7-0.89: Confident, typical markers present
   - 0.5-0.69: Moderate confidence, some ambiguity
   - Below 0.5: Low confidence, flag for human review
5. If confidence is below 0.7, flag for human review
6. Provide clear reasoning for your classification
7. Identify sub-types when possible (e.g., "employment_agreement", "nda", "purchase_order")

Be thorough and precise. Legal document classification is critical for downstream analysis."""

# JSON schema for structured output
CLASSIFIER_SCHEMA = {
    "type": "object",
    "properties": {
        "document_type": {
            "type": "string",
            "enum": [
                "email", "contract", "deposition", "pleading", 
                "medical_record", "correspondence", "financial",
                "discovery_response", "exhibit", "other"
            ],
            "description": "The classified document type"
        },
        "confidence": {
            "type": "number",
            "minimum": 0.0,
            "maximum": 1.0,
            "description": "Confidence score for the classification"
        },
        "reasoning": {
            "type": "string",
            "description": "Detailed explanation of why this classification was chosen"
        },
        "sub_type": {
            "type": "string",
            "description": "More specific document sub-type if identifiable (e.g., 'employment_agreement', 'nda')"
        },
        "key_markers": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of key markers or patterns that led to this classification"
        },
        "needs_review": {
            "type": "boolean",
            "description": "Whether this document should be flagged for human review due to low confidence"
        }
    },
    "required": ["document_type", "confidence", "reasoning"]
}


class DocumentClassifier(BaseAgent):
    """
    Agent 1: Classifies legal documents into predefined categories.
    """
    
    def __init__(self):
        # Use Haiku for fast, cost-effective classification
        model_id = os.getenv("MODEL_CLASSIFIER", "anthropic.claude-haiku-4-20250514-v1:0")
        super().__init__(name="DocumentClassifier", model_id=model_id)
    
    def run(self, state: dict) -> dict:
        """
        Classify the document and return updated state fields.
        
        Args:
            state: Pipeline state containing raw_text
            
        Returns:
            dict: Updated state with classification results
        """
        try:
            logger.info(f"Classifying document for job {state.get('job_id')}")
            
            raw_text = state.get("raw_text", "")
            if not raw_text:
                logger.warning("No raw_text provided for classification")
                return {
                    "document_type": DocumentType.OTHER,
                    "classification_confidence": 0.0,
                    "classification_reasoning": "No document text provided",
                    "document_sub_type": None
                }
            
            # Truncate very long documents for classification (first 8000 chars should be enough)
            text_sample = raw_text[:8000] if len(raw_text) > 8000 else raw_text
            
            user_prompt = f"""Analyze and classify this legal document:

{text_sample}

Provide a structured classification with confidence score, reasoning, and any identifiable sub-type."""
            
            # Call Claude with structured output
            result = self._call_claude_structured(
                system_prompt=CLASSIFIER_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                schema=CLASSIFIER_SCHEMA
            )
            
            # Extract and validate results
            document_type = result.get("document_type", "other")
            confidence = result.get("confidence", 0.0)
            reasoning = result.get("reasoning", "")
            sub_type = result.get("sub_type")
            
            logger.info(
                f"Classification complete: {document_type} "
                f"(confidence: {confidence:.2f}, sub_type: {sub_type})"
            )
            
            # Flag for review if confidence is low
            if confidence < 0.7:
                logger.warning(
                    f"Low confidence classification ({confidence:.2f}) - "
                    f"flagging for human review"
                )
            
            return {
                "document_type": DocumentType(document_type),
                "classification_confidence": confidence,
                "classification_reasoning": reasoning,
                "document_sub_type": sub_type
            }
            
        except Exception as e:
            logger.error(f"Classification failed: {str(e)}")
            return {
                "document_type": DocumentType.OTHER,
                "classification_confidence": 0.0,
                "classification_reasoning": f"Classification error: {str(e)}",
                "document_sub_type": None
            }
