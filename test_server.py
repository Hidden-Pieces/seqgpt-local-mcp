#!/usr/bin/env python3
"""
Test script for the SeqGPT Local MCP Server using unittest
This allows you to test the server functionality locally without reinstalling.

Usage:
python test_server.py                    # Test against remote server
python test_server.py --local            # Test against local server
"""

import os
import sys
import tempfile
import json
import unittest
import argparse
from pathlib import Path

# Add the server directory to the path so we can import the main module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))

from main import upload_file, hello, create_random_csv, csv_sql_query, preview_csv

# Global server URL - defaults to remote, can be overridden with --local flag
SERVER_BASE_URL = "https://seqgpt-server-for-mcp-761250691807.us-central1.run.app"

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
    
    def test_upload_file_success(self):
        """Test the upload_file tool with a real server"""
        print(f"Note: Make sure your server is running on {SERVER_BASE_URL}/upload")
        
        # Create a temporary test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is a test file for upload functionality.\n")
            f.write("Testing the MCP server upload capability.\n")
            test_file_path = f.name
        
        try:
            result = upload_file(
                file_path=test_file_path,
                server_url=f"{SERVER_BASE_URL}/upload"
            )
            
            self.assertIsInstance(result, dict)
            self.assertIn("success", result)
            
            print(f"Upload result: {json.dumps(result, indent=2)}")
            
            if result.get('success'):
                print("✅ Upload test passed!")
            else:
                print(f"❌ Upload test failed: {result.get('error', 'Unknown error')}")
                print(f"💡 Make sure your server is running on {SERVER_BASE_URL}/upload")
                # Don't fail the test if server is not running
                self.skipTest("Server not available - upload test skipped")
                
        except Exception as e:
            print(f"❌ Upload test failed with exception: {e}")
            print(f"💡 Make sure your server is running on {SERVER_BASE_URL}/upload")
            self.skipTest(f"Upload test failed: {e}")
        finally:
            # Clean up the test file
            os.unlink(test_file_path)
    
    def test_upload_file_nonexistent(self):
        """Test upload_file with a non-existent file"""
        result = upload_file(
            file_path="/nonexistent/file.txt",
            server_url=f"{SERVER_BASE_URL}/upload"
        )
        
        self.assertIsInstance(result, dict)
        self.assertFalse(result.get('success', True))
        self.assertIn("error", result)
        self.assertIn("File not found", result["error"])
    
    def test_create_random_csv(self):
        """Test the create_random_csv tool"""
        print(f"Note: Make sure your server is running on {SERVER_BASE_URL}/create-random-csv")
        
        result = create_random_csv(
            num_rows=5,
            columns=["ID", "Name", "Value"],
            server_url=f"{SERVER_BASE_URL}/create-random-csv"
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn("success", result)
        self.assertIn("server_url", result)
        self.assertIn("request_data", result)
        
        print(f"Create random CSV result: {json.dumps(result, indent=2)}")
        
        if result.get('success'):
            print("✅ Create random CSV test passed!")
        else:
            print(f"❌ Create random CSV test failed: {result.get('error', 'Unknown error')}")
            print(f"💡 Make sure your server is running on {SERVER_BASE_URL}/create-random-csv")
            self.fail(f"Create random CSV test failed: {result.get('error', 'Unknown error')}")
    
    def test_preview_csv(self):
        """Test the preview_csv tool"""
        print("Note: Make sure your server is running on both endpoints")
        
        # Step 1: Create a CSV file first
        print("Step 1: Creating CSV file...")
        create_result = create_random_csv(
            num_rows=8,
            columns=["ID", "Name", "Value"],
            server_url=f"{SERVER_BASE_URL}/create-random-csv"
        )
        
        self.assertIsInstance(create_result, dict)
        self.assertIn("success", create_result)
        
        if not create_result.get('success'):
            self.fail(f"Failed to create CSV: {create_result.get('error', 'Unknown error')}")
        
        # Extract GCS URL from the response
        response_data = json.loads(create_result["response"])
        gcs_url = response_data.get("url")
        
        if not gcs_url:
            self.fail("No GCS URL returned from create-random-csv endpoint")
        
        print(f"Created CSV file at: {gcs_url}")
        
        # Step 2: Preview the CSV file
        print("Step 2: Previewing CSV file...")
        result = preview_csv(
            gcs_url=gcs_url,
            lines=5,
            server_url=f"{SERVER_BASE_URL}/preview-csv"
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn("success", result)
        self.assertIn("server_url", result)
        self.assertIn("gcs_url", result)
        self.assertIn("lines_requested", result)
        
        print(f"Preview CSV result: {json.dumps(result, indent=2)}")
        
        if result.get('success'):
            print("✅ Preview CSV test passed!")
        else:
            print(f"❌ Preview CSV test failed: {result.get('error', 'Unknown error')}")
            print("💡 Make sure your server is running on both endpoints")
            self.fail(f"Preview CSV test failed: {result.get('error', 'Unknown error')}")
    
    def test_preview_csv_invalid_url(self):
        """Test preview_csv with invalid GCS URL"""
        result = preview_csv(
            gcs_url="invalid-url",
            lines=5,
            server_url=f"{SERVER_BASE_URL}/preview-csv"
        )
        
        self.assertIsInstance(result, dict)
        self.assertFalse(result.get('success', True))
        self.assertIn("error", result)
        self.assertIn("Invalid GCS URL", result["error"])
    
    def test_create_csv_and_preview(self):
        """Test the integration: create CSV file and then preview it"""
        print("Note: Make sure your server is running on both endpoints")
        
        # Step 1: Create a CSV file
        print("Step 1: Creating CSV file...")
        create_result = create_random_csv(
            num_rows=10,
            columns=["ID", "Name", "Value"],
            server_url=f"{SERVER_BASE_URL}/create-random-csv"
        )
        
        self.assertIsInstance(create_result, dict)
        self.assertIn("success", create_result)
        
        if not create_result.get('success'):
            self.fail(f"Failed to create CSV: {create_result.get('error', 'Unknown error')}")
        
        # Extract GCS URL from the response
        response_data = json.loads(create_result["response"])
        gcs_url = response_data.get("url")
        
        if not gcs_url:
            self.fail("No GCS URL returned from create-random-csv endpoint")
        
        print(f"Created CSV file at: {gcs_url}")
        
        # Step 2: Preview the CSV file
        print("Step 2: Previewing CSV file...")
        preview_result = preview_csv(
            gcs_url=gcs_url,
            lines=5,
            server_url=f"{SERVER_BASE_URL}/preview-csv"
        )
        
        self.assertIsInstance(preview_result, dict)
        self.assertIn("success", preview_result)
        self.assertIn("server_url", preview_result)
        self.assertIn("gcs_url", preview_result)
        
        print(f"CSV preview result: {json.dumps(preview_result, indent=2)}")
        
        if preview_result.get('success'):
            print("✅ Create CSV and preview integration test passed!")
        else:
            print(f"❌ Create CSV and preview integration test failed: {preview_result.get('error', 'Unknown error')}")
            print("💡 Make sure your server is running on both endpoints")
            self.fail(f"Create CSV and preview integration test failed: {preview_result.get('error', 'Unknown error')}")
    
    def test_create_csv_and_query(self):
        """Test the integration: create CSV file and then query it with SQL"""
        print("Note: Make sure your server is running on both endpoints")
        
        # Step 1: Create a CSV file
        print("Step 1: Creating CSV file...")
        create_result = create_random_csv(
            num_rows=5,
            columns=["ID", "Name", "Value"],
            server_url=f"{SERVER_BASE_URL}/create-random-csv"
        )
        
        self.assertIsInstance(create_result, dict)
        self.assertIn("success", create_result)
        
        if not create_result.get('success'):
            self.fail(f"Failed to create CSV: {create_result.get('error', 'Unknown error')}")
        
        # Extract GCS URL from the response
        response_data = json.loads(create_result["response"])
        gcs_url = response_data.get("url")
        
        if not gcs_url:
            self.fail("No GCS URL returned from create-random-csv endpoint")
        
        print(f"Created CSV file at: {gcs_url}")
        
        # Step 2: Query the CSV file with SQL
        print("Step 2: Querying CSV file with SQL...")
        query_result = csv_sql_query(
            sql_query="SELECT * FROM df LIMIT 3",
            gcs_url=gcs_url,
            server_url=f"{SERVER_BASE_URL}/csv-sql"
        )
        
        self.assertIsInstance(query_result, dict)
        self.assertIn("success", query_result)
        self.assertIn("server_url", query_result)
        self.assertIn("sql_query", query_result)
        
        print(f"CSV SQL query result: {json.dumps(query_result, indent=2)}")
        
        if query_result.get('success'):
            print("✅ Create CSV and query integration test passed!")
        else:
            print(f"❌ Create CSV and query integration test failed: {query_result.get('error', 'Unknown error')}")
            print("💡 Make sure your server is running on both endpoints")
            self.fail(f"Create CSV and query integration test failed: {query_result.get('error', 'Unknown error')}")

def main():
    """Run all tests"""
    parser = argparse.ArgumentParser(description="Test SeqGPT Local MCP Server")
    parser.add_argument("--local", action="store_true", 
                       help="Test against local server URLs (localhost:8000) instead of remote server")
    args = parser.parse_args()
    
    # Set server URL based on --local flag
    global SERVER_BASE_URL
    if args.local:
        SERVER_BASE_URL = "http://localhost:8000"
        print("🧪 Testing SeqGPT Local MCP Server with unittest (LOCAL MODE)")
    else:
        print("🧪 Testing SeqGPT Local MCP Server with unittest (REMOTE MODE)")
    
    print(f"Server URL: {SERVER_BASE_URL}")
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
