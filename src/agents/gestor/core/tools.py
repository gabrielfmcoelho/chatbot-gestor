import time
from typing import List, Any, Optional
from langchain_mcp_adapters.client import MultiServerMCPClient

GESTOR_API_URL = "https://mcp.gestor.sead.pi.gov.br"
MCP_TOOLS_INFO = "/mcp"

# Cache duration in seconds (5 minutes)
TOOLS_CACHE_DURATION = 300

# Global cache for tools to avoid MCP client recreation
_global_tools_cache = {}
_global_cache_timestamp = 0

async def get_tools(state: Optional[dict] = None) -> List[Any]:
    """
    Get tools from MCP with caching to avoid refetching.
    Uses global cache instead of state to avoid serialization issues.
    """
    global _global_tools_cache, _global_cache_timestamp
    current_time = time.time()
    
    # Check if we have cached tools that are still valid
    if _global_tools_cache and _global_cache_timestamp:
        time_diff = current_time - _global_cache_timestamp
        if time_diff < TOOLS_CACHE_DURATION:
            print(f"Using globally cached tools (cached {time_diff:.1f}s ago)")
            return _global_tools_cache.get("tools", [])
    
    print("Fetching tools from Gestor MCP...")
    client = MultiServerMCPClient(
        {
            "gestor": {
                # make sure you start your weather server on port 8000
                "url": f"{GESTOR_API_URL}{MCP_TOOLS_INFO}",
                "transport": "sse",
            }
        }
    )
    print("Gestor MCP client created.")
    tools = await client.get_tools()
    if not tools:
        print("No tools found in Gestor MCP.")
    else:
        print(f"Found {len(tools)} tools in Gestor MCP.")
    
    # Cache the tools globally
    _global_tools_cache = {"tools": tools}
    _global_cache_timestamp = current_time
    print("Tools cached globally")
    
    # Only store metadata in state for tracking purposes (optional)
    if state is not None and tools:
        try:
            # Store only serializable metadata
            tools_metadata = []
            for tool in tools:
                if hasattr(tool, 'name'):
                    metadata = {
                        "name": tool.name,
                        "description": getattr(tool, 'description', ''),
                        "cached_at": current_time
                    }
                    tools_metadata.append(metadata)
            
            state["cached_tools_metadata"] = tools_metadata
            state["cached_tools_timestamp"] = current_time
            print(f"Stored metadata for {len(tools_metadata)} tools in state")
        except Exception as e:
            print(f"Warning: Could not store tool metadata in state: {e}")
    
    return tools