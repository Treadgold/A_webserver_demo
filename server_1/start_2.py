import socket

# Here we send some HTML content for the first time
# We should now see something in the browser!

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

    body: bytes = b"<h1>Hello HTTP</h1>"

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
