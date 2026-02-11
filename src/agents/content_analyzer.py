"""
Agent 5: Content Analyzer
Generates comprehensive summaries, extracts key facts, identifies legal issues, and drafts narratives.
"""
from src.agents.base import BaseAgent
import logging
import os

logger = logging.getLogger(__name__)

# System prompt for content analysis
CONTENT_ANALYZER_SYSTEM_PROMPT = """You are an expert legal analyst specializing in document analysis, legal writing, and case strategy.

Your task is to provide comprehensive content analysis of legal documents, including summaries, key facts extraction, legal issue identification, and narrative drafting.

Analysis Components:

EXECUTIVE SUMMARY (2-3 paragraphs):
- Concise overview of the document
- Key parties and their relationship
- Main purpose and significance
- Critical dates and events
- Overall importance to the case

KEY FACTS (discrete, citable statements):
- Extract specific factual assertions
- Each fact should be independently citable
- Include quantitative data (dates, amounts, measurements)
- Note facts that are disputed vs. undisputed
- Highlight facts material to legal claims
- Format: Clear, declarative statements

LEGAL ISSUES:
- Identify causes of action implicated
- Note potential defenses raised
- Identify legal standards or tests mentioned
- Flag jurisdictional issues
- Note statute of limitations concerns
- Identify evidentiary issues
- Consider procedural implications

DRAFT NARRATIVE:
- Write paragraphs suitable for a brief or memo
- Use formal legal writing style
- Cite to the document appropriately
- Organize chronologically or by issue
- Include transition language
- Make it attorney-ready (minimal editing needed)
- Focus on persuasive framing where appropriate

EVIDENCE GAPS:
- Identify missing documentation referenced in the document
- Note incomplete information
- Flag areas needing further discovery
- Identify witnesses who should be deposed
- Note documents that should be requested

Document-Type Specific Analysis:
- Contracts: Focus on terms, obligations, breaches, remedies
- Depositions: Highlight admissions, inconsistencies, credibility issues
- Emails: Note tone, intent, knowledge, timing
- Pleadings: Identify claims, defenses, legal theories
- Medical Records: Extract diagnoses, treatments, causation evidence

Quality Standards:
- Be precise and cite-able
- Use legal terminology appropriately
- Maintain objectivity in summaries, advocacy in narratives
- Provide actionable insights
- Tailor analysis to document type"""

# JSON schema for structured output
CONTENT_ANALYZER_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {
            "type": "string",
            "description": "2-3 paragraph executive summary of the document"
        },
        "key_facts": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of discrete, citable factual statements"
        },
        "legal_issues": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "issue": {"type": "string", "description": "The legal issue or claim"},
                    "description": {"type": "string", "description": "Detailed explanation"},
                    "relevant_facts": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Facts supporting this issue"
                    }
                },
                "required": ["issue", "description"]
            },
            "description": "Legal issues and causes of action identified"
        },
        "draft_narrative": {
            "type": "string",
            "description": "Attorney-ready narrative paragraphs for briefs or memos"
        },
        "evidence_gaps": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "gap": {"type": "string", "description": "What's missing"},
                    "importance": {"type": "string", "enum": ["critical", "important", "helpful"]},
                    "suggested_action": {"type": "string", "description": "How to fill this gap"}
                },
                "required": ["gap", "importance"]
            },
            "description": "Identified evidence gaps and missing documentation"
        },
        "document_significance": {
            "type": "string",
            "enum": ["critical", "important", "relevant", "minimal"],
            "description": "Overall significance of this document to the case"
        },
        "recommended_tags": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Suggested tags for document organization"
        }
    },
    "required": ["summary", "key_facts", "legal_issues", "draft_narrative"]
}


class ContentAnalyzer(BaseAgent):
    """
    Agent 5: Provides comprehensive content analysis and narrative drafting.
    """
    
    def __init__(self):
        # Use Sonnet 4.5 for complex content analysis
        model_id = os.getenv("MODEL_CONTENT", "us.anthropic.claude-3-5-sonnet-20241022-v2:0")
        super().__init__(name="ContentAnalyzer", model_id=model_id)
    
    def run(self, state: dict) -> dict:
        """
        Analyze content and return updated state fields.
        
        Args:
            state: Pipeline state with raw_text, document_type, and prior agent outputs
            
        Returns:
            dict: Updated state with content analysis
        """
        try:
            logger.info(f"Analyzing content for job {state.get('job_id')}")
            
            raw_text = state.get("raw_text", "")
            document_type = state.get("document_type", "other")
            
            # Get context from prior agents
            dates = state.get("dates", [])
            people = state.get("people", [])
            entities = state.get("entities", [])
            
            if not raw_text:
                logger.warning("No raw_text provided for content analysis")
                return {
                    "summary": "No document text available for analysis",
                    "key_facts": [],
                    "legal_issues": [],
                    "draft_narrative": "",
                    "evidence_gaps": []
                }
            
            # Use substantial portion for analysis
            text_sample = raw_text[:20000] if len(raw_text) > 20000 else raw_text
            
            # Build context from prior agents
            context = f"\nDocument Type: {document_type}"
            if dates:
                context += f"\nKey Dates: {len(dates)} dates extracted"
            if people:
                context += f"\nKey People: {', '.join([p.get('name', '') for p in people[:5]])}"
            if entities:
                context += f"\nKey Entities: {', '.join([e.get('name', '') for e in entities[:5]])}"
            
            user_prompt = f"""Provide comprehensive legal analysis of this document:

{text_sample}

Context from prior analysis:{context}

Generate an executive summary, extract key facts, identify legal issues, draft narrative paragraphs, and note evidence gaps."""
            
            # Call Claude with structured output
            result = self._call_claude_structured(
                system_prompt=CONTENT_ANALYZER_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                schema=CONTENT_ANALYZER_SCHEMA,
                max_tokens=8192
            )
            
            summary = result.get("summary", "")
            key_facts = result.get("key_facts", [])
            legal_issues = result.get("legal_issues", [])
            draft_narrative = result.get("draft_narrative", "")
            evidence_gaps = result.get("evidence_gaps", [])
            
            logger.info(
                f"Content analysis complete: "
                f"{len(key_facts)} key facts, {len(legal_issues)} legal issues, "
                f"{len(evidence_gaps)} evidence gaps"
            )
            
            return {
                "summary": summary,
                "key_facts": key_facts,
                "legal_issues": legal_issues,
                "draft_narrative": draft_narrative,
                "evidence_gaps": evidence_gaps
            }
            
        except Exception as e:
            logger.error(f"Content analysis failed: {str(e)}")
            return {
                "summary": f"Analysis error: {str(e)}",
                "key_facts": [],
                "legal_issues": [],
                "draft_narrative": "",
                "evidence_gaps": []
            }
