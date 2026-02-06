"""
Base agent class with Claude API integration.
All agents inherit from this class for consistent error handling and API calls.
"""
from anthropic import Anthropic
import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class BaseAgent:
    """
    Base class for all AI agents in the pipeline.
    Handles Claude API communication and error handling.
    """
    
    def __init__(self, name: str, model: str = "claude-sonnet-4-20250514"):
        """
        Initialize the base agent.
        
        Args:
            name: Agent name for logging and identification
            model: Claude model to use (default: claude-sonnet-4-20250514)
        """
        self.name = name
        self.model = model
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        self.client = Anthropic(api_key=api_key)
        logger.info(f"Initialized {self.name} with model {self.model}")

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
        Call Claude API with text prompts.
        
        Args:
            system_prompt: System instructions for Claude
            user_prompt: User message/content to analyze
            max_tokens: Maximum tokens in response
            
        Returns:
            str: Claude's text response
        """
        try:
            logger.debug(f"{self.name}: Calling Claude API")
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"{self.name}: Claude API call failed: {str(e)}")
            raise

    def _call_claude_structured(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        schema: dict,
        max_tokens: int = 4096
    ) -> dict:
        """
        Call Claude with tool_use to get structured JSON output.
        
        Args:
            system_prompt: System instructions for Claude
            user_prompt: User message/content to analyze
            schema: JSON schema for structured output
            max_tokens: Maximum tokens in response
            
        Returns:
            dict: Structured output matching the schema
        """
        try:
            logger.debug(f"{self.name}: Calling Claude API with structured output")
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
                tools=[{
                    "name": "structured_output",
                    "description": "Return structured analysis results",
                    "input_schema": schema
                }],
                tool_choice={"type": "tool", "name": "structured_output"}
            )
            
            # Extract tool use response
            for block in response.content:
                if block.type == "tool_use":
                    logger.debug(f"{self.name}: Received structured output")
                    return block.input
            
            logger.warning(f"{self.name}: No tool_use block found in response")
            return {}
            
        except Exception as e:
            logger.error(f"{self.name}: Structured Claude API call failed: {str(e)}")
            raise
