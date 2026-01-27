import asyncio
from pathlib import Path
from typing import Callable, Optional

STATIC_DIR = Path(__file__).parent / "static"

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

# -------------------------------
# Server logic
# -------------------------------

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    request_bytes = await reader.read(1024)
    if not request_bytes:
        writer.close()
        return

    request = request_bytes.decode("utf-8", errors="ignore")
    path = parse_http_path(request)

    # --- routing logic ---
    handler = routes.get(path)
    if handler:
        body = handler()
        content_type = "text/html"  # assume HTML for routes
        response = http_response(body, content_type=content_type)
    else:
        # fallback: serve static file if it exists
        body = load_static_file(path)
        if body:
            content_type = get_content_type(resolve_file_path(path))
            response = http_response(body, content_type=content_type)
        else:
            body = b"<h1>404 Not Found</h1>"
            response = http_response(body, status="404 Not Found", content_type="text/html")

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
