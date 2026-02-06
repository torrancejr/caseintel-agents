"""
Base agent class with AWS Bedrock integration for Claude models.
All agents inherit from this class for consistent error handling and API calls.
"""
import boto3
import json
import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class BaseAgent:
    """
    Base class for all AI agents in the pipeline.
    Handles AWS Bedrock Claude API communication and error handling.
    """
    
    def __init__(self, name: str, model_id: Optional[str] = None):
        """
        Initialize the base agent with AWS Bedrock.
        
        Args:
            name: Agent name for logging and identification
            model_id: Bedrock model ID (e.g., anthropic.claude-sonnet-4-5-20250929-v1:0)
                     If None, uses default Sonnet 4.5 model
        """
        self.name = name
        self.model_id = model_id or "anthropic.claude-sonnet-4-5-20250929-v1:0"
        
        # Initialize Bedrock client
        try:
            self.client = boto3.client(
                "bedrock-runtime",
                region_name=os.getenv("AWS_REGION", "us-east-1"),
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
            )
            logger.info(f"Initialized {self.name} with Bedrock model {self.model_id}")
        except Exception as e:
            logger.error(f"Failed to initialize Bedrock client: {str(e)}")
            raise

    def run(self, state: dict) -> dict:
        """
        Execute the agent's logic. Override in subclasses.
        
        Args:
            state: Current pipeline state
            
        Returns:
            dict: Updated state fields from this agent
        """
        raise NotImplementedError(f"{self.name} must implement run() method")

    def _call_claude(self, system_prompt: str, user_prompt: str, max_tokens: int = 4096) -> str:
        """
        Call Claude via AWS Bedrock with text prompts.
        
        Args:
            system_prompt: System instructions for Claude
            user_prompt: User message/content to analyze
            max_tokens: Maximum tokens in response
            
        Returns:
            str: Claude's text response
        """
        try:
            logger.debug(f"{self.name}: Calling Bedrock Claude API")
            
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "system": system_prompt,
                "messages": [{"role": "user", "content": user_prompt}]
            })
            
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=body
            )
            
            result = json.loads(response["body"].read())
            return result["content"][0]["text"]
            
        except Exception as e:
            logger.error(f"{self.name}: Bedrock API call failed: {str(e)}")
            raise

    def _call_claude_structured(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        schema: dict,
        max_tokens: int = 4096
    ) -> dict:
        """
        Call Claude via Bedrock with tool_use to get structured JSON output.
        
        Args:
            system_prompt: System instructions for Claude
            user_prompt: User message/content to analyze
            schema: JSON schema for structured output
            max_tokens: Maximum tokens in response
            
        Returns:
            dict: Structured output matching the schema
        """
        try:
            logger.debug(f"{self.name}: Calling Bedrock Claude API with structured output")
            
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "system": system_prompt,
                "messages": [{"role": "user", "content": user_prompt}],
                "tools": [{
                    "name": "structured_output",
                    "description": "Return structured analysis results",
                    "input_schema": schema
                }],
                "tool_choice": {"type": "tool", "name": "structured_output"}
            })
            
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=body
            )
            
            result = json.loads(response["body"].read())
            
            # Extract tool use response
            for block in result.get("content", []):
                if block.get("type") == "tool_use":
                    logger.debug(f"{self.name}: Received structured output")
                    return block.get("input", {})
            
            logger.warning(f"{self.name}: No tool_use block found in response")
            return {}
            
        except Exception as e:
            logger.error(f"{self.name}: Structured Bedrock API call failed: {str(e)}")
            raise
