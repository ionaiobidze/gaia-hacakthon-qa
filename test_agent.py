#!/usr/bin/env python3
"""
Simple test script to verify the AI agent functionality.
Run this to test tool execution and conversation flow.
"""

import os
from core.engine import AIClient

def test_tools_without_api():
    """Test tool execution without requiring OpenAI API"""
    print("Testing tool execution without OpenAI API...")
    
    client = AIClient()
    
    # Test read_files tool
    print("\n1. Testing read_files tool:")
    try:
        result = client.exec_tool("read_files", {"paths": ["core/engine.py", "core/generator.py"]})
        print(f"✓ read_files executed successfully, found {len(result)} files")
        for file in result:
            print(f"  - {file['path']}: worthy={file.get('worthy', False)}")
    except Exception as e:
        print(f"✗ read_files failed: {e}")
    
    # Test pick_files tool
    print("\n2. Testing pick_files tool:")
    try:
        result = client.exec_tool("pick_files", {"paths": ["core/engine.py", "core/generator.py", "README.md", "test.txt"]})
        print(f"✓ pick_files executed successfully, picked {len(result)} files:")
        for file in result:
            print(f"  - {file}")
    except Exception as e:
        print(f"✗ pick_files failed: {e}")
    
    # Test summary tool
    print("\n3. Testing summary tool:")
    try:
        test_content = """
def test_function():
    assert True
    expect(result).toBe(expected)
    mock.verify()
"""
        result = client.exec_tool("summary", {"content": test_content})
        print(f"✓ summary executed successfully: {result}")
    except Exception as e:
        print(f"✗ summary failed: {e}")

def test_conversation_context():
    """Test conversation context management"""
    print("\n\nTesting conversation context...")
    
    client = AIClient()
    
    # Test adding messages
    client.context.add_user_message("Hello")
    client.context.add_assistant_message("Hi there!")
    client.context.add_system_message("You are a helpful assistant")
    
    messages = client.get_conversation_history()
    print(f"✓ Conversation has {len(messages)} messages")
    
    # Test metadata
    client.set_metadata("test_key", "test_value")
    value = client.get_metadata("test_key")
    print(f"✓ Metadata set and retrieved: {value}")
    
    # Test clearing
    client.clear_conversation()
    messages_after = client.get_conversation_history()
    print(f"✓ Conversation cleared, now has {len(messages_after)} messages")

def test_with_api():
    """Test with OpenAI API (requires API key)"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\n\nSkipping API test - no OPENAI_API_KEY environment variable found")
        print("To test with API, set: export OPENAI_API_KEY='your-key'")
        return
    
    print("\n\nTesting with OpenAI API...")
    
    try:
        client = AIClient(api_key=api_key, model="gpt-3.5-turbo")
        
        # Simple test call
        result = client.call("List 3 Python files that might need tests")
        print(f"✓ API call successful")
        print(f"Response: {result['response'][:100]}...")
        
    except Exception as e:
        print(f"✗ API test failed: {e}")

if __name__ == "__main__":
    print("=== AI Agent Test Suite ===")
    
    test_tools_without_api()
    test_conversation_context()
    test_with_api()
    
    print("\n=== Test Complete ===")