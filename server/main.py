"""SeqGPT Local MCP Server
Tools: upload_file, generate_data_table
Resource: hello://helper

Usage:
python server.py # stdio mode
MCP_TRANSPORT=streamable-http python server.py # http mode
"""

from __future__ import annotations
import os
import random
import tempfile
import urllib.request
import urllib.parse
import urllib.error
from mcp.server.fastmcp import FastMCP


mcp = FastMCP("seqgpt-local-mcp")


@mcp.tool(title="Upload File", description="Upload a file to the local server at localhost:8000/upload")
def upload_file(
    file_path: str,
    server_url: str = "http://localhost:8000/upload"
) -> dict:
    """
    Upload a file to the local server.
    
    Args:
        file_path: Path to the file to upload
        server_url: URL of the upload endpoint (default: http://localhost:8000/upload)
    
    Returns:
        Dictionary containing the upload response
    """
    try:
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
            "status_code": e.code
        }
    except urllib.error.URLError as e:
        return {
            "success": False,
            "error": f"URL error: {str(e.reason)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Upload failed: {str(e)}"
        }


@mcp.tool(title="Generate Data Table", description="Generate a data table with random values")
def generate_data_table(
    num_rows: int = 10,
    columns: list[str] | None = None,
    value_min: float = 0.0,
    value_max: float = 100.0
) -> dict:
    """
    Generate a data table with random values.
    
    Args:
        num_rows: Number of rows to generate (default: 10)
        columns: List of column names. If None, defaults to ["ID", "Value A", "Value B", "Value C"]
        value_min: Minimum value for random data (default: 0.0)
        value_max: Maximum value for random data (default: 100.0)
    
    Returns:
        Dictionary containing the table data in a structured format
    """
    if columns is None:
        columns = ["ID", "Value A", "Value B", "Value C"]
    rows = []
    for i in range(num_rows):
        row = {}
        for j, col_name in enumerate(columns):
            if j == 0 or col_name.lower() in ["id", "index", "row"]:
                row[col_name] = i + 1
            else:
                row[col_name] = round(random.uniform(value_min, value_max), 2)
        rows.append(row)
    return {
        "table_data": {
            "columns": columns,
            "rows": rows,
            "num_rows": num_rows,
            "num_columns": len(columns)
        },
        "summary": f"Generated table with {num_rows} rows and {len(columns)} columns"
    }


@mcp.resource("hello://helper", title="Hello resource")
def hello() -> str:
    return "Hello from SeqGPT Local MCP! I can upload files and generate data tables."


def main() -> None:
    transport = os.environ.get("MCP_TRANSPORT", "stdio")
    if transport == "streamable-http":
        mcp.run(transport="streamable-http")
    else:
        mcp.run()


if __name__ == "__main__":
    main()