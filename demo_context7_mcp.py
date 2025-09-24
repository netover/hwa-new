#!/usr/bin/env python3
"""
Demo script to test Context7 MCP server capabilities.
This script demonstrates how to use the Context7 MCP tools:
1. resolve-library-id: Resolves a general library name into a Context7-compatible library ID
2. get-library-docs: Fetches documentation for a library using a Context7-compatible library ID
"""

import subprocess
import json
import sys
import time
from typing import Dict, Any, Optional

class Context7MCPDemo:
    def __init__(self):
        self.server_process = None
        
    def start_mcp_server(self) -> subprocess.Popen:
        """Start the Context7 MCP server in stdio mode."""
        print("🚀 Starting Context7 MCP server...")
        try:
            # Start the MCP server with stdio transport (Windows compatible)
            process = subprocess.Popen(
                ["cmd", "/c", "npx", "-y", "@upstash/context7-mcp", "--transport", "stdio"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=0,
                shell=False
            )
            print("✅ Context7 MCP server started successfully!")
            return process
        except Exception as e:
            print(f"❌ Failed to start MCP server: {e}")
            sys.exit(1)
    
    def send_mcp_request(self, process: subprocess.Popen, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send a request to the MCP server and get the response."""
        try:
            # Send the request
            request_json = json.dumps(request) + "\n"
            print(f"📤 Sending request: {json.dumps(request, indent=2)}")
            
            process.stdin.write(request_json)
            process.stdin.flush()
            
            # Read the response
            response_line = process.stdout.readline()
            if response_line:
                response = json.loads(response_line.strip())
                print(f"📥 Received response: {json.dumps(response, indent=2)}")
                return response
            else:
                print("❌ No response received from server")
                return None
                
        except Exception as e:
            print(f"❌ Error communicating with MCP server: {e}")
            return None
    
    def test_resolve_library_id(self, process: subprocess.Popen, library_name: str):
        """Test the resolve-library-id tool."""
        print(f"\n🔍 Testing resolve-library-id for '{library_name}'...")
        
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "resolve-library-id",
                "arguments": {
                    "libraryName": library_name
                }
            }
        }
        
        response = self.send_mcp_request(process, request)
        if response and "result" in response:
            print(f"✅ Successfully resolved library ID for '{library_name}'")
            return response["result"]
        else:
            print(f"❌ Failed to resolve library ID for '{library_name}'")
            return None
    
    def test_get_library_docs(self, process: subprocess.Popen, library_id: str, topic: Optional[str] = None):
        """Test the get-library-docs tool."""
        print(f"\n📚 Testing get-library-docs for '{library_id}'...")
        
        arguments = {
            "context7CompatibleLibraryID": library_id,
            "tokens": 2000  # Limit tokens for demo
        }
        
        if topic:
            arguments["topic"] = topic
            print(f"🎯 Focusing on topic: '{topic}'")
        
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "get-library-docs",
                "arguments": arguments
            }
        }
        
        response = self.send_mcp_request(process, request)
        if response and "result" in response:
            print(f"✅ Successfully retrieved documentation for '{library_id}'")
            return response["result"]
        else:
            print(f"❌ Failed to retrieve documentation for '{library_id}'")
            return None
    
    def test_list_tools(self, process: subprocess.Popen):
        """Test listing available tools."""
        print("\n🛠️  Testing tools/list...")
        
        request = {
            "jsonrpc": "2.0",
            "id": 0,
            "method": "tools/list"
        }
        
        response = self.send_mcp_request(process, request)
        if response and "result" in response:
            print("✅ Successfully listed available tools:")
            tools = response["result"].get("tools", [])
            for tool in tools:
                print(f"  - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
            return response["result"]
        else:
            print("❌ Failed to list tools")
            return None
    
    def run_demo(self):
        """Run the complete demo."""
        print("🎯 Context7 MCP Server Demo")
        print("=" * 50)
        
        # Start the MCP server
        process = self.start_mcp_server()
        
        try:
            # Give the server a moment to start
            time.sleep(2)
            
            # Test 1: List available tools
            self.test_list_tools(process)
            
            # Test 2: Resolve library ID for a popular library
            library_name = "fastapi"
            resolved_result = self.test_resolve_library_id(process, library_name)
            
            # Test 3: Get documentation for a known library
            # Using a common library ID format
            library_id = "/fastapi/fastapi"  # Common format for Context7
            docs_result = self.test_get_library_docs(process, library_id, topic="routing")
            
            # Test 4: Try another library
            print("\n" + "="*50)
            print("🔄 Testing with another library...")
            
            library_name2 = "react"
            resolved_result2 = self.test_resolve_library_id(process, library_name2)
            
            if resolved_result2 and "content" in resolved_result2:
                # Try to extract a library ID from the response
                content = resolved_result2["content"]
                if isinstance(content, list) and len(content) > 0:
                    # Look for library ID in the response
                    for item in content:
                        if isinstance(item, dict) and "text" in item:
                            text = item["text"]
                            if "/react" in text.lower():
                                # Extract a potential library ID
                                library_id2 = "/facebook/react"
                                docs_result2 = self.test_get_library_docs(library_id2, topic="hooks")
                                break
            
            print("\n🎉 Demo completed successfully!")
            
        except KeyboardInterrupt:
            print("\n⏹️  Demo interrupted by user")
        except Exception as e:
            print(f"\n❌ Demo failed with error: {e}")
        finally:
            # Clean up
            if process:
                print("\n🧹 Cleaning up...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                print("✅ MCP server stopped")

def main():
    """Main function to run the demo."""
    demo = Context7MCPDemo()
    demo.run_demo()

if __name__ == "__main__":
    main()
