import asyncio
from pathlib import Path

#STATIC_DIR: Path = Path(__file__).parent / "static"

# Path to the project root (one level above this file)
PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent

# Path to the static directory at the project root
STATIC_DIR: Path = PROJECT_ROOT / "static"

# Explicit mapping from file extensions to HTTP Content-Type headers
MIME_TYPES: dict[str, str] = {
    ".html": "text/html",
    ".css": "text/css",
    ".js": "application/javascript",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".svg": "image/svg+xml",
}


def parse_http_path(request: str) -> str:
    """
    Extract the requested path from the HTTP request line.
    """
    lines = request.splitlines()
    if not lines:
        return "/"

    parts = lines[0].split()
    if len(parts) != 3:
        return "/"

    _, path, _ = parts
    return path


def get_content_type(file_path: Path) -> str:
    """
    Determine the Content-Type header based on file extension.
    """
    extension: str = file_path.suffix.lower()

    if extension in MIME_TYPES:
        return MIME_TYPES[extension]

    return "application/octet-stream"


def http_response(
    body: bytes,
    status: str = "200 OK",
    content_type: str = "text/html",
) -> bytes:
    """
    Build a minimal HTTP response.
    """
    headers: str = (
        f"HTTP/1.1 {status}\r\n"
        f"Content-Type: {content_type}\r\n"
        f"Content-Length: {len(body)}\r\n"
        "\r\n"
    )

    return headers.encode("utf-8") + body


def resolve_request_path(request_path: str) -> Path:
    """
    Convert a URL path into a filesystem path.

    - "/" maps to "index.html"
    - Paths without extensions are treated as HTML pages
    """
    if request_path == "/":
        request_path = "/index.html"
    else:
        if not Path(request_path).suffix:
            request_path += ".html"

    return STATIC_DIR / request_path.lstrip("/")


async def handle_client(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
) -> None:
    """
    Handle a single HTTP request using asyncio streams.
    """
    request_bytes: bytes = await reader.read(1024)
    if not request_bytes:
        writer.close()
        return

    request: str = request_bytes.decode("utf-8", errors="ignore")
    path: str = parse_http_path(request)

    file_path: Path = resolve_request_path(path)

    if file_path.exists() and file_path.is_file():
        body: bytes = file_path.read_bytes()
        content_type: str = get_content_type(file_path)
        response: bytes = http_response(body, content_type=content_type)
    else:
        body = b"<h1>404 Not Found</h1>"
        response = http_response(
            body,
            status="404 Not Found",
            content_type="text/html",
        )

    writer.write(response)
    await writer.drain()
    writer.close()


async def main() -> None:
    """
    Run an asyncio-based HTTP server.
    """
    server = await asyncio.start_server(
        handle_client,
        host="127.0.0.1",
        port=8002,
    )

    addr = server.sockets[0].getsockname()
    print(f"Serving on http://{addr[0]}:{addr[1]}")
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
