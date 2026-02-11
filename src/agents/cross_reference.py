"""
Agent 6: Cross-Reference Engine
Links documents to related documents, builds timeline, and maps witness mentions.
"""
from src.agents.base import BaseAgent
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

# System prompt for cross-referencing
CROSS_REFERENCE_SYSTEM_PROMPT = """You are an expert legal document cross-reference analyst specializing in connecting documents, building timelines, and tracking witness consistency.

Your task is to analyze a document in the context of other case documents and identify relationships, timeline events, and witness mentions.

Analysis Components:

DOCUMENT RELATIONSHIPS:
- Identify documents that reference or relate to the current document
- Classify relationship types:
  * "supports" - corroborates facts or claims
  * "contradicts" - conflicts with information
  * "references" - explicitly mentions or cites
  * "related_to" - same subject matter or parties
  * "part_of_chain" - email thread, contract amendment series
- Score relevance (0.0-1.0)
- Explain the relationship

TIMELINE EVENTS:
- Extract events with specific dates
- Create timeline entries with:
  * Date (ISO 8601 format)
  * Event description (clear, concise)
  * Source document reference
  * Source page/location
- Organize chronologically
- Note event significance

WITNESS MENTIONS:
- Track all people mentioned across documents
- For each witness, compile:
  * All documents where they appear
  * Context of each appearance
  * Page references
  * Role in each document
- Build witness appearance map

CONSISTENCY ANALYSIS:
- Compare witness statements across documents
- Flag contradictions or inconsistencies
- Note evolving stories or changing testimony
- Identify impeachment opportunities
- Examples:
  * Deposition says "no knowledge" but email shows they were informed
  * Contract signature but later claims never saw the document
  * Timeline contradictions

Cross-Reference Guidelines:
1. Be thorough in identifying relationships
2. Cite specific passages that establish connections
3. Quantify relevance scores based on strength of connection
4. Flag significant contradictions prominently
5. Build comprehensive witness appearance tracking
6. Create actionable timeline events
7. Note document chains (email threads, amendment series)

When provided with related document summaries from the vector database, analyze them for connections to the current document."""

# JSON schema for structured output
CROSS_REFERENCE_SCHEMA = {
    "type": "object",
    "properties": {
        "related_documents": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "doc_id": {"type": "string", "description": "Related document ID"},
                    "title": {"type": "string", "description": "Document title or description"},
                    "relevance": {
                        "type": "number",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "description": "Relevance score"
                    },
                    "relationship": {
                        "type": "string",
                        "enum": ["supports", "contradicts", "references", "related_to", "part_of_chain"],
                        "description": "Type of relationship"
                    },
                    "explanation": {
                        "type": "string",
                        "description": "How these documents are related"
                    }
                },
                "required": ["doc_id", "relevance", "relationship", "explanation"]
            },
            "description": "Documents related to the current document"
        },
        "timeline_events": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "date": {"type": "string", "description": "ISO 8601 date (YYYY-MM-DD)"},
                    "event": {"type": "string", "description": "Event description"},
                    "source_doc": {"type": "string", "description": "Source document ID"},
                    "source_page": {"type": ["integer", "null"], "description": "Page number"},
                    "significance": {
                        "type": "string",
                        "enum": ["critical", "important", "notable"],
                        "description": "Event significance"
                    }
                },
                "required": ["date", "event", "source_doc"]
            },
            "description": "Timeline events extracted from this document"
        },
        "witness_mentions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Witness name"},
                    "appearances": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "doc_id": {"type": "string"},
                                "context": {"type": "string"},
                                "page": {"type": ["integer", "null"]}
                            },
                            "required": ["doc_id", "context"]
                        },
                        "description": "All appearances of this witness"
                    }
                },
                "required": ["name", "appearances"]
            },
            "description": "Witness mention tracking"
        },
        "consistency_flags": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "witness": {"type": "string", "description": "Witness name"},
                    "issue": {"type": "string", "description": "Description of inconsistency"},
                    "documents": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Document IDs showing the inconsistency"
                    },
                    "severity": {
                        "type": "string",
                        "enum": ["critical", "significant", "minor"],
                        "description": "Severity of inconsistency"
                    }
                },
                "required": ["witness", "issue", "documents"]
            },
            "description": "Witness consistency issues identified"
        }
    },
    "required": ["timeline_events", "witness_mentions"]
}


class CrossReferenceEngine(BaseAgent):
    """
    Agent 6: Cross-references documents and builds case-wide connections.
    """
    
    def __init__(self, rag_retriever=None):
        """
        Initialize with optional RAG retriever for document similarity search.
        Uses Haiku 4.5 for cost-effective cross-referencing.
        
        Args:
            rag_retriever: Optional RAG retrieval service for finding related documents
        """
        model_id = os.getenv("MODEL_CROSSREF", "us.anthropic.claude-3-5-haiku-20241022-v1:0")
        super().__init__(name="CrossReferenceEngine", model_id=model_id)
        self.rag_retriever = rag_retriever
    
    def run(self, state: dict) -> dict:
        """
        Cross-reference document and return updated state fields.
        
        Args:
            state: Pipeline state with all prior agent outputs
            
        Returns:
            dict: Updated state with cross-reference analysis
        """
        try:
            logger.info(f"Cross-referencing document for job {state.get('job_id')}")
            
            raw_text = state.get("raw_text", "")
            case_id = state.get("case_id", "")
            job_id = state.get("job_id", "")
            
            # Get context from prior agents
            summary = state.get("summary", "")
            dates = state.get("dates", [])
            people = state.get("people", [])
            
            if not raw_text:
                logger.warning("No raw_text provided for cross-referencing")
                return self._empty_result()
            
            # Retrieve related documents from RAG if available
            related_docs_context = ""
            if self.rag_retriever and summary:
                try:
                    related_docs = self.rag_retriever.find_related_documents(
                        case_id=case_id,
                        query_text=summary,
                        top_k=5,
                        exclude_doc_id=job_id
                    )
                    if related_docs:
                        related_docs_context = "\n\nRelated documents in this case:\n"
                        for doc in related_docs:
                            related_docs_context += f"- {doc.get('title', 'Untitled')}: {doc.get('summary', '')}\n"
                except Exception as e:
                    logger.warning(f"RAG retrieval failed: {str(e)}")
            
            # Build context from prior analysis
            context = f"""
Current Document Summary: {summary}

Key Dates Extracted: {len(dates)} dates
Key People: {', '.join([p.get('name', '') for p in people[:10]])}
{related_docs_context}
"""
            
            # Use portion of text for cross-referencing
            text_sample = raw_text[:12000] if len(raw_text) > 12000 else raw_text
            
            user_prompt = f"""Cross-reference this document with other case documents and build timeline/witness tracking:

{text_sample}

Context:{context}

Identify related documents, create timeline events, track witness mentions, and flag any inconsistencies."""
            
            # Call Claude with structured output
            result = self._call_claude_structured(
                system_prompt=CROSS_REFERENCE_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                schema=CROSS_REFERENCE_SCHEMA,
                max_tokens=8192
            )
            
            related_documents = result.get("related_documents", [])
            timeline_events = result.get("timeline_events", [])
            witness_mentions = result.get("witness_mentions", [])
            consistency_flags = result.get("consistency_flags", [])
            
            logger.info(
                f"Cross-reference complete: "
                f"{len(related_documents)} related docs, {len(timeline_events)} timeline events, "
                f"{len(witness_mentions)} witnesses, {len(consistency_flags)} consistency flags"
            )
            
            if consistency_flags:
                logger.warning(f"Witness consistency issues detected: {len(consistency_flags)}")
            
            return {
                "related_documents": related_documents,
                "timeline_events": timeline_events,
                "witness_mentions": witness_mentions,
                "consistency_flags": consistency_flags
            }
            
        except Exception as e:
            logger.error(f"Cross-referencing failed: {str(e)}")
            return self._empty_result()
    
    def _empty_result(self) -> dict:
        """Return empty cross-reference result."""
        return {
            "related_documents": [],
            "timeline_events": [],
            "witness_mentions": [],
            "consistency_flags": []
        }
