import socket
from pathlib import Path

#STATIC_DIR: Path = Path(__file__).parent / "static"

# Path to the project root (one level above this file)
PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent

# Path to the static directory at the project root
STATIC_DIR: Path = PROJECT_ROOT / "static"

# Minimal mapping of file extensions to Content-Type
MIME_TYPES: dict[str, str] = {
    ".html": "text/html",
    ".css": "text/css",
    ".js": "application/javascript",
    ".png": "image/png",
    ".jpg": "image/jpeg",
}


def parse_http_path(request: str) -> str:
    """
    Extract the requested path from the HTTP request line.
    """
    first_line: str = request.splitlines()[0]
    _, path, _ = first_line.split()
    return path


def build_http_response(
    body: bytes,
    status: str,
    content_type: str,
) -> bytes:
    """
    Build a minimal HTTP response from parts.
    """
    headers: str = (
        f"HTTP/1.1 {status}\r\n"
        f"Content-Type: {content_type}\r\n"
        f"Content-Length: {len(body)}\r\n"
        "\r\n"
    )
    return headers.encode("utf-8") + body


def handle_client(client_socket: socket.socket) -> None:
    """
    Handle a single HTTP request.
    """
    request_bytes: bytes = client_socket.recv(1024)
    if not request_bytes:
        client_socket.close()
        return

    request: str = request_bytes.decode("utf-8", errors="ignore")
    path: str = parse_http_path(request)

    # Map URL to filesystem
    if path == "/":
        file_path: Path = STATIC_DIR / "index.html"
    else:
        file_path = STATIC_DIR / path.lstrip("/")

    if file_path.exists() and file_path.is_file():
        body: bytes = file_path.read_bytes()

        extension: str = file_path.suffix.lower()
        content_type: str = MIME_TYPES.get(
            extension,
            "application/octet-stream",
        )

        response: bytes = build_http_response(
            body=body,
            status="200 OK",
            content_type=content_type,
        )
    else:
        body = b"<h1>404 Not Found</h1>"
        response = build_http_response(
            body=body,
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

    print("Serving on http://127.0.0.1:8002")
    print("Press Ctrl+C to stop")

    try:
        while True:
            client_socket, addr = server_socket.accept()
            print(f"Connection from {addr}")
            handle_client(client_socket)
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server_socket.close()


if __name__ == "__main__":
    main()
