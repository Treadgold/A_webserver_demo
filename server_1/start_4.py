import socket
from pathlib import Path

# Introduce static file serving
# Explain headers contain mime type
# fails to close on ctrl+c

#STATIC_DIR: Path = Path(__file__).parent / "static"

# Path to the project root (one level above this file)
PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent

# Path to the static directory at the project root
STATIC_DIR: Path = PROJECT_ROOT / "static"


def parse_http_path(request: str) -> str:
    first_line: str = request.splitlines()[0]
    _, path, _ = first_line.split()
    return path


def main() -> None:
    server_socket: socket.socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM,
    )
    server_socket.bind(("127.0.0.1", 8002))
    server_socket.listen(5)

    print("Serving on http://127.0.0.1:8002")

    while True:
        client_socket, addr = server_socket.accept()
        request_bytes: bytes = client_socket.recv(1024)
        request: str = request_bytes.decode("utf-8", errors="ignore")

        path: str = parse_http_path(request)

        if path == "/":
            file_path: Path = STATIC_DIR / "index.html"
        else:
            file_path = STATIC_DIR / path.lstrip("/")

        if file_path.exists():
            body: bytes = file_path.read_bytes()
            response: bytes = (
                b"HTTP/1.1 200 OK\r\n"
                b"Content-Type: text/html\r\n"
                b"Content-Length: " + str(len(body)).encode("utf-8") + b"\r\n"
                b"\r\n"
                + body
            )
        else:
            body = b"<h1>404 Not Found</h1>"
            response = (
                b"HTTP/1.1 404 Not Found\r\n"
                b"Content-Type: text/html\r\n"
                b"Content-Length: " + str(len(body)).encode("utf-8") + b"\r\n"
                b"\r\n"
                + body
            )

        client_socket.sendall(response)
        client_socket.close()


if __name__ == "__main__":
    main()
