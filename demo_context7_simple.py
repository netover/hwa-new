#!/usr/bin/env python3
"""
Simple demo script to test Context7 MCP server capabilities.
This demonstrates the two main tools:
1. resolve-library-id: Find Context7-compatible library IDs
2. get-library-docs: Get documentation for libraries
"""

import subprocess
import json
import sys
import time

def run_mcp_command(tool_name, arguments):
    """Run a single MCP command and return the result."""
    print(f"\n🔧 Testing {tool_name}...")
    print(f"📋 Arguments: {json.dumps(arguments, indent=2)}")
    
    try:
        # Create the MCP request
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        # Start the MCP server process
        process = subprocess.Popen(
            ["cmd", "/c", "npx", "-y", "@upstash/context7-mcp", "--transport", "stdio"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace'  # Handle encoding issues gracefully
        )
        
        # Send request and get response
        request_json = json.dumps(request) + "\n"
        stdout, stderr = process.communicate(input=request_json, timeout=30)
        
        if process.returncode == 0 and stdout:
            # Parse the response
            lines = stdout.strip().split('\n')
            for line in lines:
                if line.strip() and line.strip().startswith('{'):
                    try:
                        response = json.loads(line.strip())
                        if "result" in response:
                            print(f"✅ Success! Tool {tool_name} executed successfully")
                            return response["result"]
                    except json.JSONDecodeError:
                        continue
        
        print(f"❌ Failed to execute {tool_name}")
        if stderr:
            print(f"Error: {stderr[:200]}...")
        return None
        
    except subprocess.TimeoutExpired:
        print(f"⏰ Timeout executing {tool_name}")
        process.kill()
        return None
    except Exception as e:
        print(f"❌ Error executing {tool_name}: {e}")
        return None

def demo_resolve_library():
    """Demo the resolve-library-id tool."""
    print("\n" + "="*60)
    print("🔍 DEMO: Resolve Library ID")
    print("="*60)
    
    library_name = "fastapi"
    result = run_mcp_command("resolve-library-id", {"libraryName": library_name})
    
    if result and "content" in result:
        content = result["content"]
        if isinstance(content, list) and len(content) > 0:
            text_content = content[0].get("text", "")
            # Extract first few lines to show the result
            lines = text_content.split('\n')[:10]
            print(f"📄 Found documentation for '{library_name}':")
            for line in lines:
                if line.strip():
                    print(f"   {line[:100]}...")
                    break
            return True
    
    return False

def demo_get_docs():
    """Demo the get-library-docs tool."""
    print("\n" + "="*60)
    print("📚 DEMO: Get Library Documentation")
    print("="*60)
    
    # Use a known library ID format
    library_id = "/fastapi/fastapi"
    result = run_mcp_command("get-library-docs", {
        "context7CompatibleLibraryID": library_id,
        "topic": "routing",
        "tokens": 1500
    })
    
    if result and "content" in result:
        content = result["content"]
        if isinstance(content, list) and len(content) > 0:
            text_content = content[0].get("text", "")
            # Show first few lines of documentation
            lines = text_content.split('\n')[:5]
            print(f"📖 Documentation for '{library_id}' (topic: routing):")
            for line in lines:
                if line.strip():
                    print(f"   {line[:80]}...")
            return True
    
    return False

def test_server_availability():
    """Test if the Context7 MCP server is available."""
    print("🧪 Testing Context7 MCP Server Availability...")
    
    try:
        # Test with a simple tools/list request
        process = subprocess.Popen(
            ["cmd", "/c", "npx", "-y", "@upstash/context7-mcp", "--transport", "stdio"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        request = {
            "jsonrpc": "2.0",
            "id": 0,
            "method": "tools/list"
        }
        
        request_json = json.dumps(request) + "\n"
        stdout, stderr = process.communicate(input=request_json, timeout=15)
        
        if process.returncode == 0 and "resolve-library-id" in stdout:
            print("✅ Context7 MCP server is available and working!")
            return True
        else:
            print("❌ Context7 MCP server is not responding correctly")
            return False
            
    except Exception as e:
        print(f"❌ Error testing server: {e}")
        return False

def main():
    """Main demo function."""
    print("🎯 Context7 MCP Server - Simple Demo")
    print("="*60)
    print("This demo showcases the Context7 MCP server capabilities:")
    print("• resolve-library-id: Find library IDs")
    print("• get-library-docs: Get up-to-date documentation")
    print("="*60)
    
    # Test server availability
    if not test_server_availability():
        print("❌ Cannot proceed - server is not available")
        sys.exit(1)
    
    # Run demos
    success_count = 0
    
    if demo_resolve_library():
        success_count += 1
    
    if demo_get_docs():
        success_count += 1
    
    # Summary
    print("\n" + "="*60)
    print("📊 DEMO SUMMARY")
    print("="*60)
    print(f"✅ Successful tests: {success_count}/2")
    
    if success_count == 2:
        print("🎉 All Context7 MCP server capabilities demonstrated successfully!")
        print("\n💡 Key Features Demonstrated:")
        print("   • Library ID resolution for popular frameworks")
        print("   • Up-to-date documentation retrieval")
        print("   • Topic-focused documentation filtering")
        print("   • Integration with MCP protocol")
    else:
        print("⚠️  Some tests failed, but the server is functional")
    
    print("\n🔧 MCP Configuration:")
    print("   Server: github.com/upstash/context7-mcp")
    print("   Package: @upstash/context7-mcp")
    print("   Transport: stdio")
    print("   Status: ✅ Installed and working")

if __name__ == "__main__":
    main()
