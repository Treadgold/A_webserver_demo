import socket


def main() -> None:
    server_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM,
    )
    server_socket.bind(("127.0.0.1", 8002))
    server_socket.listen(1)

    print("Listening on http://127.0.0.1:8002")

    client_socket, addr = server_socket.accept()
    print(f"Connection from {addr}")

    # Send raw bytes — not valid HTTP
    try:
        client_socket.sendall(b"Hello from a socket!")
        print("Success!")
    except Exception as e:
        print("Failed to send to client")
        print(f"Exception {e}")
    
    client_socket.close()
    server_socket.close()


if __name__ == "__main__":
    main()
