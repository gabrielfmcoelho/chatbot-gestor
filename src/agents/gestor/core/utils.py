import json
import hashlib
import logging
from typing import Any, cast
from typing import List, Dict
from requests import get
from langchain_core.language_models.base import LanguageModelInput
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage
from langchain_core.runnables import Runnable, RunnableLambda, RunnableSerializable
from agents.gestor.core.tools import get_tools

from .states import GestorState

logger = logging.getLogger(__name__)

# Constants for response size management
MAX_RESPONSE_SIZE = 5000  # Maximum characters for a tool response
MAX_TOTAL_CONTEXT_SIZE = 50000  # Maximum total context size

def _prepare_messages(state: GestorState, system_prompt: BaseMessage) -> list[BaseMessage]:
    """Helper function to prepare messages for the model."""
    return [system_prompt] + state.get("messages", [])

def wrap_model(
    model: BaseChatModel | Runnable[LanguageModelInput, Any], system_prompt: BaseMessage
) -> RunnableSerializable[GestorState, Any]:
    """Wrapper for the model with state preprocessing."""
    try:
        print("Wrapping model with tools and preprocessor...")
        preprocessor = RunnableLambda(
            lambda state: _prepare_messages(cast(GestorState, state), system_prompt),
            name="StateModifier",
        )
        print("Model wrapped with tools and preprocessor.")
        return preprocessor | model  # type: ignore[return-value]
    except Exception as e:
        print(f"Error wrapping model: {e}")
        raise

def get_last_user_message(state: GestorState) -> str:
    """Extract the last user message from state."""
    if state.get("messages"):
        for msg in reversed(state["messages"]):
            if isinstance(msg, HumanMessage):
                return str(msg.content)
    return ""

def build_conversation_context(state: GestorState) -> str:
    """Build a conversation context string from the state."""
    if not state.get("messages"):
        return ""
    
    context = []
    for msg in state["messages"]:
        # ignore the last message
        if isinstance(msg, HumanMessage):
            context.append(f"Usuário: {msg.content}")
        else:
            context.append(f"Assistente: {msg.content}")
    
    return "\n".join(context)

def generate_tool_call_id(tool_name: str, tool_args: dict) -> str:
    """Generate a unique ID for a tool call to prevent duplicates."""
    content = f"{tool_name}:{json.dumps(tool_args, sort_keys=True)}"
    return hashlib.md5(content.encode()).hexdigest()

def is_response_too_large(content: str) -> bool:
    """Check if a response is too large for the context window."""
    return len(content) > MAX_RESPONSE_SIZE

def summarize_large_response(content: str, tool_name: str) -> str:
    """Summarize a large response to prevent context window overflow."""
    if not is_response_too_large(content):
        return content
    
    try:
        # Try to parse as JSON and extract key information
        if content.strip().startswith('{') or content.strip().startswith('['):
            data = json.loads(content)
            if isinstance(data, dict):
                # Extract key fields for summarization
                summary_parts = []
                for key, value in list(data.items())[:5]:  # Limit to first 5 keys
                    if isinstance(value, (str, int, float, bool)):
                        summary_parts.append(f"{key}: {value}")
                    elif isinstance(value, list):
                        summary_parts.append(f"{key}: lista com {len(value)} items")
                    elif isinstance(value, dict):
                        summary_parts.append(f"{key}: objeto com {len(value)} campos")
                
                summary = f"Resposta da ferramenta {tool_name} (resumida - {len(content)} chars):\n"
                summary += "\n".join(summary_parts)
                if len(data) > 5:
                    summary += f"\n... e mais {len(data) - 5} campos"
                return summary
            
            elif isinstance(data, list):
                summary = f"Resposta da ferramenta {tool_name} (resumida - {len(content)} chars):\n"
                summary += f"Lista com {len(data)} items"
                if len(data) > 0:
                    first_item = data[0]
                    if isinstance(first_item, dict):
                        summary += f"\nPrimeiro item: {list(first_item.keys())[:3]}"
                    else:
                        summary += f"\nPrimeiro item: {str(first_item)[:100]}"
                return summary
    
    except json.JSONDecodeError:
        pass
    
    # Fallback: truncate and add summary info
    truncated = content[:MAX_RESPONSE_SIZE - 200]
    summary = f"Resposta da ferramenta {tool_name} (truncada - original: {len(content)} chars):\n"
    summary += truncated + "\n\n[... resposta truncada devido ao tamanho]"
    
    return summary

def manage_context_size(state: GestorState) -> GestorState:
    """Manage the total context size by summarizing or removing old messages."""
    messages = state.get("messages", [])
    
    # Calculate total context size
    total_size = sum(len(str(msg.content)) for msg in messages if hasattr(msg, 'content'))
    
    if total_size <= MAX_TOTAL_CONTEXT_SIZE:
        return state
    
    logger.info(f"Context size ({total_size}) exceeds limit, managing size...")
    
    # Keep the last user message and recent AI responses
    important_messages = []
    
    # Find the last user message and keep it with context
    for i, message in enumerate(reversed(messages)):
        if isinstance(message, HumanMessage):
            # Keep this message and a few before it
            start_idx = max(0, len(messages) - i - 3)
            important_messages = messages[start_idx:]
            break
    
    # If we still have too much context, summarize tool messages
    if sum(len(str(msg.content)) for msg in important_messages if hasattr(msg, 'content')) > MAX_TOTAL_CONTEXT_SIZE:
        managed_messages = []
        for msg in important_messages:
            if isinstance(msg, ToolMessage) and hasattr(msg, 'content'):
                if is_response_too_large(msg.content):
                    # Create summarized tool message
                    summarized_content = summarize_large_response(msg.content, msg.name)
                    summarized_msg = ToolMessage(
                        content=summarized_content,
                        tool_call_id=msg.tool_call_id,
                        name=msg.name
                    )
                    managed_messages.append(summarized_msg)
                else:
                    managed_messages.append(msg)
            else:
                managed_messages.append(msg)
        
        state["messages"] = managed_messages
    else:
        state["messages"] = important_messages
    
    new_total_size = sum(len(str(msg.content)) for msg in state["messages"] if hasattr(msg, 'content'))
    logger.info(f"Context size reduced from {total_size} to {new_total_size}")
    
    return state

def clean_state_for_serialization(state: GestorState) -> GestorState:
    """
    Clean state to ensure it contains only serializable objects.
    Removes any tool objects or other non-serializable data.
    """
    # Create a copy to avoid modifying the original
    cleaned_state = dict(state)
    
    # Remove any potential non-serializable objects
    keys_to_check = ['tools_responses', 'cached_tools']
    for key in keys_to_check:
        if key in cleaned_state:
            # If it contains tool objects, remove it
            try:
                import json
                json.dumps(cleaned_state[key])  # Test if serializable
            except (TypeError, ValueError):
                print(f"Removing non-serializable field: {key}")
                del cleaned_state[key]
    
    return cleaned_state


