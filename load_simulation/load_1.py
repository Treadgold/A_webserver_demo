import socket
import threading

HOST = "127.0.0.1"
PORT = 8002
NUM_CLIENTS = 100

def fetch(i: int):
    try:
        with socket.create_connection((HOST, PORT), timeout=5) as sock:
            sock.sendall(b"GET /index.html HTTP/1.1\r\nHost: localhost\r\n\r\n")
            resp = sock.recv(1024)
            print(f"Client {i} received {len(resp)} bytes")
    except Exception as e:
        print(f"Client {i} failed: {e}")

threads = [threading.Thread(target=fetch, args=(i,)) for i in range(NUM_CLIENTS)]
for t in threads: t.start()
for t in threads: t.join()
