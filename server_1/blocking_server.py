import socket
from pathlib import Path

# We fix our ctrl+c exit and make it clean!

# Main problem, can't handle async
# demo with load simulation

#STATIC_DIR: Path = Path(__file__).parent / "static"

# Path to the project root (one level above this file)
PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent

# Path to the static directory at the project root
STATIC_DIR: Path = PROJECT_ROOT / "static"

# Explicit mapping from file extensions to HTTP Content-Type headers
# This tells the browser how to interpret the bytes we send
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

    Example request line:
        GET /styles.css HTTP/1.1
    """
    first_line: str = request.splitlines()[0]
    _, path, _ = first_line.split()
    return path


def get_content_type(file_path: Path) -> str:
    """
    Determine the Content-Type header based on the file extension.
    """
    extension: str = file_path.suffix.lower()

    if extension in MIME_TYPES:
        return MIME_TYPES[extension]

    # Fallback for unknown or binary file types
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

    - "/" maps to "/index.html"
    - Paths without extensions are treated as HTML pages
    """
    if request_path == "/":
        request_path = "/index.html"
    else:
        # If there is no file extension, assume HTML
        if not Path(request_path).suffix:
            request_path += ".html"

    # Remove leading slash before joining with filesystem path
    return STATIC_DIR / request_path.lstrip("/")


def handle_client(client_socket: socket.socket) -> None:
    """
    Handle a single HTTP request from a client.
    """
    request_bytes: bytes = client_socket.recv(1024)
    if not request_bytes:
        client_socket.close()
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

    client_socket.sendall(response)
    client_socket.close()


def main() -> None:
    """
    Run a simple blocking HTTP server.
    """
    server_socket: socket.socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM,
    )
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("127.0.0.1", 8002))
    server_socket.listen(5)
    server_socket.settimeout(1.0)

    print("Serving on http://127.0.0.1:8002")
    print("Press Ctrl+C to stop")

    try:
        while True:
            try:
                client_socket, addr = server_socket.accept()
                print(f"Connection from {addr}")
                handle_client(client_socket)
            except socket.timeout:
                continue
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server_socket.close()


if __name__ == "__main__":
    main()
