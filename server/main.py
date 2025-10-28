"""SeqGPT Local MCP Server
Tools: upload_file, create_random_csv, csv_sql_query, preview_csv
Resource: hello://helper

Usage:
python server.py                    # stdio mode with remote server
python server.py --local            # stdio mode with local server
MCP_TRANSPORT=streamable-http python server.py --local  # http mode with local server
"""

from __future__ import annotations
import os
import random
import tempfile
import json
import urllib.request
import urllib.parse
import urllib.error
import argparse

# ---- vendor hook (safe) ----
import sys, pathlib, os
HERE = pathlib.Path(__file__).resolve().parent
LIB = HERE / "lib"
if LIB.exists():
    sys.path.insert(0, str(LIB))
# Optional: guard against old Pythons early (before importing anything heavy)
import sys
if sys.version_info < (3, 10):
    print("SeqGPT MCP requires Python 3.10+ (detected %s). Please install Python 3.11/3.12." % sys.version, file=sys.stderr)
    raise SystemExit(1)
# Optional: scrub noisy env vars (belt & suspenders)
for k in ("PYTHONHOME","PYTHONPATH","CONDA_PREFIX","CONDA_PYTHON_EXE","CONDA_DEFAULT_ENV","CONDA_SHLVL"):
    os.environ.pop(k, None)
from mcp.server.fastmcp import FastMCP
# ---- rest of your server ----


from mcp.server.fastmcp import FastMCP

mcp = FastMCP("seqgpt-local-mcp")

# Global server URL - defaults to remote, can be overridden with --local flag
SERVER_BASE_URL = "https://seqgpt-server-for-mcp-761250691807.us-central1.run.app"




@mcp.tool(title="Upload File", description="Upload a file to the server")
def upload_file(
    file_path: str,
    server_url: str | None = None
) -> dict:
    """
    Upload a file to the server.
    
    Args:
        file_path: Path to the file to upload
        server_url: URL of the upload endpoint (defaults to SERVER_BASE_URL/upload)
    
    Returns:
        Dictionary containing the upload response
    """
    try:
        if server_url is None:
            server_url = f"{SERVER_BASE_URL}/upload"
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": f"File not found: {file_path}"
            }
        
        # Read the file
        with open(file_path, 'rb') as file:
            file_data = file.read()
        
        # Get filename from path
        filename = os.path.basename(file_path)
        
        # Create multipart form data
        boundary = '----WebKitFormBoundary' + ''.join([str(random.randint(0, 9)) for _ in range(16)])
        
        # Build the multipart body
        body_parts = []
        body_parts.append(f'--{boundary}'.encode())
        body_parts.append(f'Content-Disposition: form-data; name="file"; filename="{filename}"'.encode())
        body_parts.append(b'Content-Type: application/octet-stream')
        body_parts.append(b'')
        body_parts.append(file_data)
        body_parts.append(f'--{boundary}--'.encode())
        
        body = b'\r\n'.join(body_parts)
        
        # Create request
        req = urllib.request.Request(
            server_url,
            data=body,
            method='POST'
        )
        req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')
        req.add_header('Content-Length', str(len(body)))
        
        # Make the request
        with urllib.request.urlopen(req, timeout=30) as response:
            response_data = response.read().decode('utf-8')
            
        return {
            "success": True,
            "status_code": response.status,
            "response": response_data,
            "file_path": file_path,
            "server_url": server_url
        }
    except urllib.error.HTTPError as e:
        return {
            "success": False,
            "error": f"HTTP error {e.code}: {e.reason}",
            "status_code": e.code,
            "server_url": server_url
        }
    except urllib.error.URLError as e:
        return {
            "success": False,
            "error": f"URL error: {str(e.reason)}",
            "server_url": server_url
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Upload failed: {str(e)}",
            "server_url": server_url
        }


@mcp.tool(title="Create Random CSV", description="Create a random CSV file using the server endpoint")
def create_random_csv(
    num_rows: int = 10,
    columns: list[str] | None = None,
    server_url: str | None = None
) -> dict:
    """
    Create a random CSV file using the server endpoint.
    
    Args:
        num_rows: Number of rows to generate (default: 10)
        columns: List of column names. If None, defaults to ["ID", "Value A", "Value B", "Value C"]
        server_url: URL of the create-random-csv endpoint (defaults to SERVER_BASE_URL/create-random-csv)
    
    Returns:
        Dictionary containing the response from the server
    """
    try:
        if server_url is None:
            server_url = f"{SERVER_BASE_URL}/create-random-csv"
        data = {"rows": num_rows}
        if columns is not None:
            data["columns"] = columns
        
        # Convert to JSON
        json_data = json.dumps(data).encode('utf-8')
        
        # Create request
        req = urllib.request.Request(
            server_url,
            data=json_data,
            method='POST'
        )
        req.add_header('Content-Type', 'application/json')
        req.add_header('Content-Length', str(len(json_data)))
        
        # Make the request
        with urllib.request.urlopen(req, timeout=30) as response:
            response_data = response.read().decode('utf-8')
            
        return {
            "success": True,
            "status_code": response.status,
            "response": response_data,
            "server_url": server_url,
            "request_data": data
        }
    except urllib.error.HTTPError as e:
        return {
            "success": False,
            "error": f"HTTP error {e.code}: {e.reason}",
            "status_code": e.code,
            "server_url": server_url
        }
    except urllib.error.URLError as e:
        return {
            "success": False,
            "error": f"URL error: {str(e.reason)}",
            "server_url": server_url
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Create random CSV failed: {str(e)}",
            "server_url": server_url
        }


@mcp.tool(title="CSV SQL Query", description="Execute SQL query on CSV data using the server endpoint")
def csv_sql_query(
    sql_query: str,
    gcs_url: str | None = None,
    csv_data: str | None = None,
    table_name: str | None = None,
    server_url: str | None = None
) -> dict:
    """
    Execute SQL query on CSV data using the server endpoint.
    
    Args:
        sql_query: SQL query to execute
        gcs_url: GCS URL of the CSV file (optional, takes precedence over csv_data)
        csv_data: CSV data as string (optional, if not provided server may use default data)
        table_name: Name of the table to use in SQL queries (optional, defaults to 'df')
        server_url: URL of the csv-sql endpoint (defaults to SERVER_BASE_URL/csv-sql)
    
    Returns:
        Dictionary containing the query results
    """
    try:
        if server_url is None:
            server_url = f"{SERVER_BASE_URL}/csv-sql"
        # Prepare the request data
        data = {
            "sql_query": sql_query
        }
        
        if gcs_url:
            # Extract filename from GCS URL for input_file_path
            if not gcs_url.startswith("gs://"):
                raise ValueError("Invalid GCS URL")
            filename = gcs_url.split("gs://")[-1]
            _, filename = filename.split("/", 1)  # Remove bucket name
            data["input_file_path"] = filename
        elif csv_data:
            data["csv_data"] = csv_data
        
        if table_name:
            data["table_name"] = table_name
        
        # Convert to JSON
        json_data = json.dumps(data).encode('utf-8')
        
        # Create request
        req = urllib.request.Request(
            server_url,
            data=json_data,
            method='POST'
        )
        req.add_header('Content-Type', 'application/json')
        req.add_header('Content-Length', str(len(json_data)))
        
        # Make the request
        with urllib.request.urlopen(req, timeout=30) as response:
            response_data = response.read().decode('utf-8')
            
        return {
            "success": True,
            "status_code": response.status,
            "response": response_data,
            "server_url": server_url,
            "sql_query": sql_query
        }
    except urllib.error.HTTPError as e:
        return {
            "success": False,
            "error": f"HTTP error {e.code}: {e.reason}",
            "status_code": e.code,
            "server_url": server_url,
            "sql_query": sql_query
        }
    except urllib.error.URLError as e:
        return {
            "success": False,
            "error": f"URL error: {str(e.reason)}",
            "server_url": server_url,
            "sql_query": sql_query
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"CSV SQL query failed: {str(e)}",
            "server_url": server_url,
            "sql_query": sql_query
        }


@mcp.tool(title="Preview CSV", description="Preview CSV file data using the server endpoint")
def preview_csv(
    gcs_url: str,
    lines: int = 10,
    server_url: str | None = None
) -> dict:
    """
    Preview CSV file data from GCS.
    
    Args:
        gcs_url: GCS URL of the CSV file to preview
        lines: Number of lines to preview (max 1000, defaults to 10)
        server_url: URL of the preview-csv endpoint (defaults to SERVER_BASE_URL/preview-csv)
    
    Returns:
        Dictionary containing the CSV preview data
    """
    try:
        if server_url is None:
            server_url = f"{SERVER_BASE_URL}/preview-csv"
        if not gcs_url.startswith("gs://"):
            raise ValueError("Invalid GCS URL")
        filename = gcs_url.split("gs://")[-1]
        _, filename = filename.split("/", 1)  # Remove bucket name
        
        # Prepare the request data
        data = {
            "input_file_path": filename,
            "lines": min(lines, 1000)  # Cap at 1000 lines as per server limit
        }
        
        # Convert to JSON
        json_data = json.dumps(data).encode('utf-8')
        
        # Create request
        req = urllib.request.Request(
            server_url,
            data=json_data,
            method='POST'
        )
        req.add_header('Content-Type', 'application/json')
        req.add_header('Content-Length', str(len(json_data)))
        
        # Make the request
        with urllib.request.urlopen(req, timeout=30) as response:
            response_data = response.read().decode('utf-8')
            
        return {
            "success": True,
            "status_code": response.status,
            "response": response_data,
            "server_url": server_url,
            "gcs_url": gcs_url,
            "lines_requested": lines
        }
    except urllib.error.HTTPError as e:
        return {
            "success": False,
            "error": f"HTTP error {e.code}: {e.reason}",
            "status_code": e.code,
            "server_url": server_url,
            "gcs_url": gcs_url
        }
    except urllib.error.URLError as e:
        return {
            "success": False,
            "error": f"URL error: {str(e.reason)}",
            "server_url": server_url,
            "gcs_url": gcs_url
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Preview CSV failed: {str(e)}",
            "server_url": server_url,
            "gcs_url": gcs_url
        }


@mcp.resource("hello://helper", title="Hello resource")
def hello() -> str:
    return "Hello from SeqGPT Local MCP! I can upload files and generate data tables."


def main() -> None:
    parser = argparse.ArgumentParser(description="SeqGPT Local MCP Server")
    parser.add_argument("--local", action="store_true", 
                       help="Use local server URLs (localhost:8000) instead of remote server")
    args = parser.parse_args()
    
    # Set server URL based on --local flag
    global SERVER_BASE_URL
    if args.local:
        SERVER_BASE_URL = "http://localhost:8000"
        print("Using local server URLs")
    else:
        print(f"Using remote server URL: {SERVER_BASE_URL}")
    
    transport = os.environ.get("MCP_TRANSPORT", "stdio")
    if transport == "streamable-http":
        mcp.run(transport="streamable-http")
    else:
        mcp.run()


if __name__ == "__main__":
    main()