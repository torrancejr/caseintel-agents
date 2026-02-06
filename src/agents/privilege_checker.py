"""
Agent 3: Privilege Checker
Scans for attorney-client privilege, work product, and confidentiality issues.
"""
from src.agents.base import BaseAgent
from src.workflows.state import PrivilegeFlag
import logging
import os

logger = logging.getLogger(__name__)

# System prompt for privilege checking
PRIVILEGE_SYSTEM_PROMPT = """You are an expert legal privilege reviewer with deep knowledge of attorney-client privilege, work product doctrine, and confidentiality protections.

Your task is to identify potential privilege issues in legal documents.

Privilege Categories:

ATTORNEY-CLIENT PRIVILEGE:
- Communications between attorney and client
- Legal advice sought or provided
- Confidential communications for legal representation
- In-house counsel communications (when acting as legal advisor, not business advisor)
- Look for: "attorney-client privileged", communications to/from attorneys, legal advice

WORK PRODUCT DOCTRINE:
- Documents prepared in anticipation of litigation
- Attorney mental impressions, strategies, legal theories
- Litigation preparation materials
- Investigation reports prepared by counsel
- Look for: legal analysis, case strategy, litigation plans, "work product"

CONFIDENTIAL:
- Documents marked as confidential
- Trade secrets, proprietary information
- Settlement negotiations (may be protected)
- Look for: "CONFIDENTIAL", "PROPRIETARY", confidentiality markings

Detection Guidelines:
1. Examine document headers, footers, and watermarks for privilege markings
2. Analyze sender/recipient patterns (attorney ↔ client)
3. Identify legal advice vs. business advice
4. Look for litigation preparation context
5. Check for explicit privilege assertions
6. Consider document type context (emails between counsel are more likely privileged)
7. ERR ON THE SIDE OF CAUTION - when in doubt, flag as potentially privileged
8. Provide specific excerpts that triggered privilege concerns
9. Return confidence score (0.0-1.0)
10. Recommend human review for borderline cases

Important Considerations:
- Not all attorney communications are privileged (business advice, factual information)
- Privilege can be waived by disclosure to third parties
- Crime-fraud exception: communications in furtherance of crime/fraud are not privileged
- Look for inadvertent disclosure indicators

Provide detailed reasoning and specific excerpts supporting your determination."""

# JSON schema for structured output
PRIVILEGE_SCHEMA = {
    "type": "object",
    "properties": {
        "privilege_flags": {
            "type": "array",
            "items": {
                "type": "string",
                "enum": ["attorney_client", "work_product", "confidential", "none"]
            },
            "description": "List of applicable privilege types"
        },
        "confidence": {
            "type": "number",
            "minimum": 0.0,
            "maximum": 1.0,
            "description": "Confidence in privilege determination"
        },
        "reasoning": {
            "type": "string",
            "description": "Detailed explanation of privilege determination"
        },
        "privileged_excerpts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Excerpt that indicates privilege"},
                    "type": {"type": "string", "description": "Type of privilege indicated"},
                    "page": {"type": ["integer", "null"], "description": "Page number"}
                },
                "required": ["text", "type"]
            },
            "description": "Specific excerpts that indicate privilege"
        },
        "recommendation": {
            "type": "string",
            "enum": ["clearly_privileged", "likely_privileged", "review_required", "not_privileged"],
            "description": "Recommendation for handling this document"
        },
        "waiver_concerns": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Any concerns about privilege waiver (e.g., third party recipients)"
        }
    },
    "required": ["privilege_flags", "confidence", "reasoning", "recommendation"]
}


class PrivilegeChecker(BaseAgent):
    """
    Agent 3: Checks for privilege and confidentiality issues.
    """
    
    def __init__(self):
        # Use Sonnet 4.5 for complex privilege analysis
        model_id = os.getenv("MODEL_PRIVILEGE", "anthropic.claude-sonnet-4-5-20250929-v1:0")
        super().__init__(name="PrivilegeChecker", model_id=model_id)
    
    def run(self, state: dict) -> dict:
        """
        Check for privilege issues and return updated state fields.
        
        Args:
            state: Pipeline state containing raw_text and document_type
            
        Returns:
            dict: Updated state with privilege analysis
        """
        try:
            logger.info(f"Checking privilege for job {state.get('job_id')}")
            
            raw_text = state.get("raw_text", "")
            document_type = state.get("document_type", "other")
            
            if not raw_text:
                logger.warning("No raw_text provided for privilege checking")
                return {
                    "privilege_flags": [PrivilegeFlag.NONE],
                    "privilege_reasoning": "No document text provided",
                    "privilege_confidence": 0.0,
                    "privileged_excerpts": [],
                    "privilege_recommendation": "not_privileged"
                }
            
            # Use first 12000 chars for privilege checking
            text_sample = raw_text[:12000] if len(raw_text) > 12000 else raw_text
            
            user_prompt = f"""Analyze this {document_type} document for privilege and confidentiality issues:

{text_sample}

Identify any attorney-client privilege, work product, or confidentiality concerns.
Err on the side of caution - flag potential privilege issues for review."""
            
            # Call Claude with structured output
            result = self._call_claude_structured(
                system_prompt=PRIVILEGE_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                schema=PRIVILEGE_SCHEMA,
                max_tokens=6144
            )
            
            # Extract and convert privilege flags
            privilege_flags_raw = result.get("privilege_flags", ["none"])
            privilege_flags = [PrivilegeFlag(flag) for flag in privilege_flags_raw]
            
            confidence = result.get("confidence", 0.0)
            reasoning = result.get("reasoning", "")
            excerpts = result.get("privileged_excerpts", [])
            recommendation = result.get("recommendation", "review_required")
            
            # Log privilege findings
            if PrivilegeFlag.NONE not in privilege_flags:
                logger.warning(
                    f"Privilege flags detected: {privilege_flags} "
                    f"(confidence: {confidence:.2f}, recommendation: {recommendation})"
                )
            else:
                logger.info("No privilege issues detected")
            
            return {
                "privilege_flags": privilege_flags,
                "privilege_reasoning": reasoning,
                "privilege_confidence": confidence,
                "privileged_excerpts": excerpts,
                "privilege_recommendation": recommendation
            }
            
        except Exception as e:
            logger.error(f"Privilege checking failed: {str(e)}")
            # On error, err on the side of caution
            return {
                "privilege_flags": [PrivilegeFlag.NONE],
                "privilege_reasoning": f"Privilege check error: {str(e)}",
                "privilege_confidence": 0.0,
                "privileged_excerpts": [],
                "privilege_recommendation": "review_required"
            }
