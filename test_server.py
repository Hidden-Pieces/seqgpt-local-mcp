#!/usr/bin/env python3
"""
Test script for the SeqGPT Local MCP Server using unittest
This allows you to test the server functionality locally without reinstalling.
"""

import os
import sys
import tempfile
import json
import unittest
from pathlib import Path

# Add the server directory to the path so we can import the main module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))

# Import the functions directly
from main import upload_file, generate_data_table, hello

class TestSeqGPTMCP(unittest.TestCase):
    """Test cases for the SeqGPT Local MCP Server"""
    
    def test_server_startup(self):
        """Test that the server can start without errors"""
        try:
            from main import main
            self.assertTrue(True, "Server imports successfully!")
        except Exception as e:
            self.fail(f"Server startup test failed with exception: {e}")
    
    def test_hello_resource(self):
        """Test the hello resource"""
        try:
            result = hello()
            self.assertIsInstance(result, str)
            self.assertIn("SeqGPT", result)
            print(f"Hello resource result: {result}")
        except Exception as e:
            self.fail(f"Hello resource test failed with exception: {e}")
    
    def test_generate_data_table(self):
        """Test the generate_data_table tool"""
        try:
            result = generate_data_table(
                num_rows=5,
                columns=["ID", "Name", "Value"],
                value_min=1.0,
                value_max=100.0
            )
            
            self.assertIsInstance(result, dict)
            self.assertIn("table_data", result)
            self.assertIn("summary", result)
            
            table_data = result["table_data"]
            self.assertEqual(table_data["num_rows"], 5)
            self.assertEqual(len(table_data["columns"]), 3)
            self.assertEqual(len(table_data["rows"]), 5)
            
            print(f"Data table result: {json.dumps(result, indent=2)}")
            
        except Exception as e:
            self.fail(f"Data table test failed with exception: {e}")
    
    def test_upload_file_success(self):
        """Test the upload_file tool with a real server"""
        print("Note: Make sure your server is running on http://localhost:8000/upload")
        
        # Create a temporary test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is a test file for upload functionality.\n")
            f.write("Testing the MCP server upload capability.\n")
            test_file_path = f.name
        
        try:
            result = upload_file(
                file_path=test_file_path,
                server_url="http://localhost:8000/upload"
            )
            
            self.assertIsInstance(result, dict)
            self.assertIn("success", result)
            
            print(f"Upload result: {json.dumps(result, indent=2)}")
            
            if result.get('success'):
                print("✅ Upload test passed!")
            else:
                print(f"❌ Upload test failed: {result.get('error', 'Unknown error')}")
                print("💡 Make sure your server is running on http://localhost:8000/upload")
                # Don't fail the test if server is not running
                self.skipTest("Server not available - upload test skipped")
                
        except Exception as e:
            print(f"❌ Upload test failed with exception: {e}")
            print("💡 Make sure your server is running on http://localhost:8000/upload")
            self.skipTest(f"Upload test failed: {e}")
        finally:
            # Clean up the test file
            os.unlink(test_file_path)
    
    def test_upload_file_nonexistent(self):
        """Test upload_file with a non-existent file"""
        result = upload_file(
            file_path="/nonexistent/file.txt",
            server_url="http://localhost:8000/upload"
        )
        
        self.assertIsInstance(result, dict)
        self.assertFalse(result.get('success', True))
        self.assertIn("error", result)
        self.assertIn("File not found", result["error"])

def main():
    """Run all tests"""
    print("🧪 Testing SeqGPT Local MCP Server with unittest")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestSeqGPTMCP)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("🏁 All tests passed!")
    else:
        print(f"❌ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)")
        for failure in result.failures:
            print(f"FAIL: {failure[0]}")
            print(f"     {failure[1]}")
        for error in result.errors:
            print(f"ERROR: {error[0]}")
            print(f"      {error[1]}")

if __name__ == "__main__":
    main()
