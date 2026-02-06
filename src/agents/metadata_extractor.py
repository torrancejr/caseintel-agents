"""
Agent 2: Metadata Extractor
Extracts dates, people, entities, and locations from legal documents.
"""
from src.agents.base import BaseAgent
import logging
import os

logger = logging.getLogger(__name__)

# System prompt for metadata extraction
METADATA_SYSTEM_PROMPT = """You are an expert legal document analyst specializing in metadata extraction.

Your task is to extract ALL dates, people, entities, and locations from legal documents with precise source citations.

Extraction Guidelines:

DATES:
- Extract every date mentioned in any format
- Normalize to ISO 8601 format (YYYY-MM-DD)
- Include surrounding context (what happened on this date)
- Note the source page or paragraph reference
- Handle relative dates (e.g., "30 days after execution")
- Include date ranges

PEOPLE:
- Extract all person names (full names preferred)
- Infer their role where possible: plaintiff, defendant, witness, attorney, signatory, expert, judge, etc.
- Count total mentions throughout the document
- Note first appearance location
- Handle name variations (e.g., "John Smith" and "Mr. Smith")
- Include titles and credentials when present

ENTITIES:
- Extract organizations, companies, government bodies, law firms
- Classify type: corporation, LLC, government agency, law firm, etc.
- Infer their role in the case/document
- Include parent companies or affiliations when mentioned

LOCATIONS:
- Extract all geographic locations: cities, states, countries, addresses
- Include context (e.g., "governing law jurisdiction", "place of incident", "venue")
- Note specific addresses vs. general locations

Quality Standards:
1. Be comprehensive - extract ALL instances, not just the first mention
2. Deduplicate entities that appear multiple times (but count mentions)
3. Provide precise source citations (page numbers, paragraph numbers, section headers)
4. Normalize formats for consistency
5. Handle legal-specific patterns (Bates numbers, docket references)
6. Preserve exact spelling and capitalization for names

Return structured data with complete metadata for each extracted item."""

# JSON schema for structured output
METADATA_SCHEMA = {
    "type": "object",
    "properties": {
        "dates": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "date": {"type": "string", "description": "ISO 8601 formatted date (YYYY-MM-DD)"},
                    "context": {"type": "string", "description": "What happened on this date"},
                    "source_page": {"type": ["integer", "null"], "description": "Page number where found"},
                    "date_type": {"type": "string", "description": "Type of date (e.g., 'execution', 'incident', 'filing')"}
                },
                "required": ["date", "context"]
            }
        },
        "people": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Full name of the person"},
                    "role": {"type": "string", "description": "Their role (plaintiff, attorney, witness, etc.)"},
                    "mentions": {"type": "integer", "description": "Number of times mentioned"},
                    "first_appearance": {"type": "string", "description": "Where they first appear (e.g., 'page 1')"},
                    "title": {"type": ["string", "null"], "description": "Professional title or credentials"}
                },
                "required": ["name", "role", "mentions"]
            }
        },
        "entities": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Entity name"},
                    "type": {"type": "string", "description": "Entity type (corporation, LLC, government, etc.)"},
                    "role": {"type": "string", "description": "Role in the document/case"}
                },
                "required": ["name", "type", "role"]
            }
        },
        "locations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Location name or address"},
                    "context": {"type": "string", "description": "Why this location is mentioned"},
                    "location_type": {"type": "string", "description": "Type (city, state, address, venue, etc.)"}
                },
                "required": ["name", "context"]
            }
        }
    },
    "required": ["dates", "people", "entities", "locations"]
}


class MetadataExtractor(BaseAgent):
    """
    Agent 2: Extracts structured metadata from legal documents.
    """
    
    def __init__(self):
        # Use Haiku 4.5 for fast metadata extraction
        model_id = os.getenv("MODEL_METADATA", "anthropic.claude-haiku-4-5-20251001-v1:0")
        super().__init__(name="MetadataExtractor", model_id=model_id)
    
    def run(self, state: dict) -> dict:
        """
        Extract metadata and return updated state fields.
        
        Args:
            state: Pipeline state containing raw_text and document_type
            
        Returns:
            dict: Updated state with extracted metadata
        """
        try:
            logger.info(f"Extracting metadata for job {state.get('job_id')}")
            
            raw_text = state.get("raw_text", "")
            document_type = state.get("document_type", "other")
            
            if not raw_text:
                logger.warning("No raw_text provided for metadata extraction")
                return {
                    "dates": [],
                    "people": [],
                    "entities": [],
                    "locations": []
                }
            
            # For very long documents, we may need to process in chunks
            # For now, use first 16000 chars for metadata extraction
            text_sample = raw_text[:16000] if len(raw_text) > 16000 else raw_text
            
            user_prompt = f"""Extract all metadata from this {document_type} document:

{text_sample}

Extract ALL dates, people, entities, and locations with complete context and source citations.
Be thorough and comprehensive."""
            
            # Call Claude with structured output
            result = self._call_claude_structured(
                system_prompt=METADATA_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                schema=METADATA_SCHEMA,
                max_tokens=8192  # More tokens for comprehensive extraction
            )
            
            dates = result.get("dates", [])
            people = result.get("people", [])
            entities = result.get("entities", [])
            locations = result.get("locations", [])
            
            logger.info(
                f"Metadata extraction complete: "
                f"{len(dates)} dates, {len(people)} people, "
                f"{len(entities)} entities, {len(locations)} locations"
            )
            
            return {
                "dates": dates,
                "people": people,
                "entities": entities,
                "locations": locations
            }
            
        except Exception as e:
            logger.error(f"Metadata extraction failed: {str(e)}")
            return {
                "dates": [],
                "people": [],
                "entities": [],
                "locations": []
            }
