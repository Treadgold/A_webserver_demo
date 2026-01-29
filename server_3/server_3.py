import asyncio
from pathlib import Path
from typing import Callable, Optional, Dict
from dataclasses import dataclass


def find_static_dir(start: Path) -> Path:
    """
    Walk upwards until a 'static' directory is found.
    """
    for parent in [start, *start.parents]:
        candidate: Path = parent / "static"
        if candidate.is_dir():
            return candidate
    raise RuntimeError("Could not find 'static' directory")

THIS_FILE: Path = Path(__file__).resolve()
STATIC_DIR: Path = find_static_dir(THIS_FILE)


# Explicit MIME type mapping
MIME_TYPES = {
    ".html": "text/html",
    ".css": "text/css",
    ".js": "application/javascript",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".svg": "image/svg+xml",
}

# -------------------------------
# Routing dictionary & decorator
# -------------------------------

routes = {}  # path -> handler function

def route(path: str) -> Callable:
    """Register a function as a route handler for a specific path."""
    def decorator(func):
        routes[path] = func
        return func
    return decorator

# -------------------------------
# Helper functions
# -------------------------------


@dataclass
class Request:
    method: str
    path: str
    headers: Dict[str, str]
    body: bytes
    
    
async def read_http_request(
    reader: asyncio.StreamReader
) -> Request:
    """
    Read and parse a single HTTP request from the stream.
    """

    # Read headers
    header_bytes: bytes = await reader.readuntil(b"\r\n\r\n")
    header_text: str = header_bytes.decode("utf-8", errors="ignore")

    lines: list[str] = header_text.splitlines()
    method, path, _ = lines[0].split()

    headers: Dict[str, str] = {}
    for line in lines[1:]:
        if ":" in line:
            key, value = line.split(":", 1)
            headers[key.lower()] = value.strip()

    # Read body if present
    content_length: int = int(headers.get("content-length", "0"))
    body: bytes = b""

    if content_length > 0:
        body = await reader.readexactly(content_length)

    return Request(
        method=method,
        path=path,
        headers=headers,
        body=body,
    )

def parse_http_path(request: str) -> str:
    """Extract the path from the HTTP request line."""
    lines = request.splitlines()
    if not lines:
        return "/"

    parts = lines[0].split()
    if len(parts) != 3:
        return "/"

    _, path, _ = parts
    return path

def get_content_type(file_path: Path) -> str:
    """Return Content-Type header based on file extension."""
    ext = file_path.suffix.lower()
    return MIME_TYPES.get(ext, "application/octet-stream")

def resolve_file_path(request_path: str) -> Path:
    """Resolve URL path to a static file path."""
    if request_path == "/":
        request_path = "/index.html"
    elif not Path(request_path).suffix:
        request_path += ".html"

    return (STATIC_DIR / request_path.lstrip("/")).resolve()

def http_response(body: bytes, status: str = "200 OK", content_type: str = "text/html") -> bytes:
    """Build a full HTTP response with headers."""
    headers = (
        f"HTTP/1.1 {status}\r\n"
        f"Content-Type: {content_type}\r\n"
        f"Content-Length: {len(body)}\r\n"
        "\r\n"
    )
    return headers.encode("utf-8") + body

def load_static_file(path: str) -> Optional[bytes]:
    """Load a file from the static directory if it exists."""
    file_path = resolve_file_path(path)
    if not file_path.is_relative_to(STATIC_DIR.resolve()):
        return None
    if file_path.exists() and file_path.is_file():
        return file_path.read_bytes()
    return None

# -------------------------------
# Example route handlers
# -------------------------------

@route("/about")
def about_page() -> bytes:
    return load_static_file("about.html") or b"<h1>Missing about.html</h1>"

@route("/")
def index_route() -> bytes:
    return load_static_file("index.html") or b"<h1>Missing index.html</h1>"


#---------------------------------
# Message POST endpoint
#---------------------------------

@route("/submit")
def handle_form_submission() -> bytes:
        # This is a placeholder; in a real server, you'd parse the POST body
    return b"<h1>Form submitted successfully!</h1>"



# -------------------------------
# Server logic
# -------------------------------

async def handle_client(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter
) -> None:
    try:
        request: Request = await read_http_request(reader)
    except asyncio.IncompleteReadError:
        writer.close()
        return

    print(request.method, request.path)
    print("BODY:", request.body.decode("utf-8", errors="ignore"))

    handler = routes.get(request.path)

    if handler:
        response_body: bytes = handler()
        response = http_response(response_body)

    else:
        # Try static file
        body: Optional[bytes] = load_static_file(request.path)
        if body is not None:
            content_type: str = get_content_type(resolve_file_path(request.path))
            response = http_response(body, content_type=content_type)
        else:
            response = http_response(
                b"<h1>404 Not Found</h1>",
                status="404 Not Found"
            )

    writer.write(response)
    await writer.drain()
    writer.close()


async def main():
    server = await asyncio.start_server(handle_client, host="127.0.0.1", port=8002)
    addr = server.sockets[0].getsockname()
    print(f"Serving with routing on http://{addr[0]}:{addr[1]}")
    print("Press Ctrl+C to stop")

    async with server:
        try:
            await server.serve_forever()
        except asyncio.CancelledError:
            print("\nShutting down gracefully...")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server stopped.")
