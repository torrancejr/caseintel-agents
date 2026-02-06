"""
Agent 4: Hot Doc Detector
Flags documents containing smoking guns, contradictions, or case-critical content.
"""
from src.agents.base import BaseAgent
import logging

logger = logging.getLogger(__name__)

# System prompt for hot doc detection
HOT_DOC_SYSTEM_PROMPT = """You are an expert legal document analyst specializing in identifying case-critical "hot documents" - documents that contain smoking guns, key admissions, contradictions, or other highly significant content.

Your task is to identify documents that require immediate attorney attention.

Hot Document Categories:

ADMISSIONS AGAINST INTEREST:
- Party admitting fault, liability, or wrongdoing
- Acknowledgment of facts harmful to their case
- Statements contradicting their legal position
- Examples: "We knew about the defect", "I didn't follow proper procedures"

SMOKING GUNS:
- Direct evidence of wrongdoing
- Cover-up language or destruction of evidence
- Explicit acknowledgment of illegal/improper conduct
- Conspiracy or coordination evidence
- Examples: "Make sure no one finds out", "Delete those emails"

CONTRADICTIONS:
- Statements contradicting deposition testimony
- Inconsistencies with other documents in the case
- Timeline contradictions
- Conflicting accounts of key events

KEY ADMISSIONS:
- Admissions of key facts in dispute
- Acknowledgment of damages or harm
- Admission of knowledge or intent
- Concessions on material issues

CRITICAL EVIDENCE:
- Documents proving causation
- Evidence of damages
- Proof of notice or knowledge
- Documentation of key events

IMPEACHMENT MATERIAL:
- Evidence contradicting witness statements
- Prior inconsistent statements
- Evidence of bias or motive to lie

Severity Levels:
- CRITICAL: Immediate attorney review required, case-changing evidence
- HIGH: Significant evidence, flag for priority review
- MEDIUM: Notable but not case-critical, include in analysis

Scoring Guidelines:
- 0.9-1.0: Smoking gun, game-changing evidence
- 0.7-0.89: Strong hot doc, significant admissions or contradictions
- 0.5-0.69: Moderate importance, worth flagging
- Below 0.5: Not a hot doc

For each hot doc flag:
1. Provide the exact excerpt (with page reference)
2. Explain why it's significant
3. Identify the type of hot doc issue
4. Assess severity and potential impact
5. Note any contradictions with known case facts

Be precise and cite specific text. This analysis guides attorney strategy."""

# JSON schema for structured output
HOT_DOC_SCHEMA = {
    "type": "object",
    "properties": {
        "is_hot_doc": {
            "type": "boolean",
            "description": "Whether this document contains hot doc content"
        },
        "score": {
            "type": "number",
            "minimum": 0.0,
            "maximum": 1.0,
            "description": "Hot doc score (0.0 = not hot, 1.0 = critical smoking gun)"
        },
        "severity": {
            "type": "string",
            "enum": ["critical", "high", "medium", "low"],
            "description": "Severity level for attorney review prioritization"
        },
        "flags": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": [
                            "admission", "smoking_gun", "contradiction", 
                            "key_admission", "critical_evidence", "impeachment"
                        ],
                        "description": "Type of hot doc issue"
                    },
                    "excerpt": {
                        "type": "string",
                        "description": "Exact text excerpt that triggered the flag"
                    },
                    "page": {
                        "type": ["integer", "null"],
                        "description": "Page number where found"
                    },
                    "reasoning": {
                        "type": "string",
                        "description": "Why this is significant and what it proves/contradicts"
                    },
                    "impact": {
                        "type": "string",
                        "description": "Potential impact on the case"
                    }
                },
                "required": ["type", "excerpt", "reasoning"]
            },
            "description": "List of specific hot doc flags with excerpts"
        },
        "summary": {
            "type": "string",
            "description": "Overall summary of why this is a hot document"
        },
        "recommended_action": {
            "type": "string",
            "description": "Recommended next steps for attorneys"
        }
    },
    "required": ["is_hot_doc", "score", "severity"]
}


class HotDocDetector(BaseAgent):
    """
    Agent 4: Detects hot documents requiring immediate attorney attention.
    """
    
    def __init__(self):
        super().__init__(name="HotDocDetector")
    
    def run(self, state: dict) -> dict:
        """
        Detect hot doc issues and return updated state fields.
        
        Args:
            state: Pipeline state containing raw_text, document_type, and metadata
            
        Returns:
            dict: Updated state with hot doc analysis
        """
        try:
            logger.info(f"Detecting hot docs for job {state.get('job_id')}")
            
            raw_text = state.get("raw_text", "")
            document_type = state.get("document_type", "other")
            case_id = state.get("case_id", "")
            
            if not raw_text:
                logger.warning("No raw_text provided for hot doc detection")
                return {
                    "is_hot_doc": False,
                    "hot_doc_reasons": [],
                    "hot_doc_score": 0.0,
                    "hot_doc_severity": "low"
                }
            
            # Use substantial portion for hot doc detection
            text_sample = raw_text[:16000] if len(raw_text) > 16000 else raw_text
            
            # Include case context if available (for contradiction detection)
            context_note = f"\n\nCase ID: {case_id}\nDocument Type: {document_type}"
            
            user_prompt = f"""Analyze this document for hot doc content - smoking guns, admissions, contradictions, or case-critical evidence:

{text_sample}{context_note}

Identify any content that would require immediate attorney attention.
Provide specific excerpts and explain their significance."""
            
            # Call Claude with structured output
            result = self._call_claude_structured(
                system_prompt=HOT_DOC_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                schema=HOT_DOC_SCHEMA,
                max_tokens=8192
            )
            
            is_hot_doc = result.get("is_hot_doc", False)
            score = result.get("score", 0.0)
            severity = result.get("severity", "low")
            flags = result.get("flags", [])
            
            if is_hot_doc:
                logger.warning(
                    f"HOT DOC DETECTED: score={score:.2f}, severity={severity}, "
                    f"flags={len(flags)}"
                )
            else:
                logger.info("No hot doc issues detected")
            
            return {
                "is_hot_doc": is_hot_doc,
                "hot_doc_reasons": flags,
                "hot_doc_score": score,
                "hot_doc_severity": severity
            }
            
        except Exception as e:
            logger.error(f"Hot doc detection failed: {str(e)}")
            return {
                "is_hot_doc": False,
                "hot_doc_reasons": [],
                "hot_doc_score": 0.0,
                "hot_doc_severity": "low"
            }
