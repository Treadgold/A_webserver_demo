import asyncio
from pathlib import Path
from typing import Callable, Optional, Dict
from dataclasses import dataclass
from urllib.parse import parse_qs, unquote_plus


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

@dataclass
class Request:
    method: str
    path: str
    headers: Dict[str, str]
    body: bytes

# Old simple routes (before method-aware routing):
# i've assigned to an unused object 'old_routes' 
# just so that you can see the nice colours
old_routes: Dict[str, Callable[[], bytes]] = {}  # path -> handler function

# New method-aware routing
routes: Dict[tuple[str, str], Callable[[Request], bytes]] = {}


def route(method: str, path: str) -> Callable:
    def decorator(func: Callable[[Request], bytes]):
        routes[(method.upper(), path)] = func
        return func
    return decorator

# -------------------------------
# Helper functions
# -------------------------------


    
    
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

@route("GET", "/about")
def about_page() -> bytes:
    return load_static_file("about.html") or b"<h1>Missing about.html</h1>"

@route("GET", "/")
def index_route() -> bytes:
    return load_static_file("index.html") or b"<h1>Missing index.html</h1>"


#---------------------------------
# Message POST endpoint
#---------------------------------

@route("POST", "/submit")
def handle_form_submission(request: Request) -> bytes:
    # Parse the POST body
    form_data = parse_qs(request.body.decode("utf-8"))
    # parse_qs returns lists of values, so we just take the first for each field
    name = unquote_plus(form_data.get("name", ["Anonymous"])[0])
    message = unquote_plus(form_data.get("message", [""])[0])

    # Build a simple HTML response including the submitted content
    response_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Form Submission Result</title>
        <style>
            body {{ font-family: sans-serif; padding: 2rem; background: #f0f0f0; }}
            .card {{
                background: #fff;
                padding: 1rem 1.5rem;
                border-radius: 0.5rem;
                box-shadow: 0 2px 6px rgba(0,0,0,0.2);
                max-width: 500px;
                margin: 2rem auto;
            }}
            .card h2 {{ margin-top: 0; color: #333; }}
            .card p {{ margin: 0.5rem 0 0 0; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h2>Thank you, {name}!</h2>
            <p>Your message was received:</p>
            <p><em>{message}</em></p>
        </div>
    </body>
    </html>
    """
    return response_html.encode("utf-8")



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

    handler = routes.get((request.method, request.path))

    if handler:
        response_body: bytes = handler(request)
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
