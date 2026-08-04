# /// script
# dependencies = [
#   "mcp-server-fetch",
#   "mcp",
# ]
# ///
import sys
import mcp.shared.exceptions

# Alias McpError / MCPError safely across different mcp SDK versions
if hasattr(mcp.shared.exceptions, "MCPError") and not hasattr(mcp.shared.exceptions, "McpError"):
    mcp.shared.exceptions.McpError = getattr(mcp.shared.exceptions, "MCPError")
if hasattr(mcp.shared.exceptions, "McpError") and not hasattr(mcp.shared.exceptions, "MCPError"):
    mcp.shared.exceptions.MCPError = getattr(mcp.shared.exceptions, "McpError")

from mcp_server_fetch import main

if __name__ == "__main__":
    main()
