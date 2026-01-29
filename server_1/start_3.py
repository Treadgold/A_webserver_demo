import socket

# Let's look at an actual request
# We will need our web server to understand
# all the different requests it might receive

def main() -> None:
    server_socket: socket.socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM,
    )
    server_socket.bind(("127.0.0.1", 8002))
    server_socket.listen(1)

    print("Listening on http://127.0.0.1:8002")

    client_socket, addr = server_socket.accept()
    print(f"Connection from {addr}")

    request_bytes: bytes = client_socket.recv(1024)
    request: str = request_bytes.decode("utf-8", errors="ignore")

    print("----- REQUEST -----")
    print(request)
    print("-------------------")

    body: bytes = b"<h1>Check the terminal</h1>"

    response: bytes = (
        b"HTTP/1.1 200 OK\r\n"
        b"Content-Type: text/html\r\n"
        b"Content-Length: " + str(len(body)).encode("utf-8") + b"\r\n"
        b"\r\n"
        + body
    )

    client_socket.sendall(response)
    client_socket.close()
    server_socket.close()


if __name__ == "__main__":
    main()
