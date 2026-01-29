import socket

# define the endpoint parameters
host = 'localhost'
port = 8080

# Create a UDP socket using IPv4
sock = socket.socket(socket.AF_INET,
                     socket.SOCK_DGRAM)
sock.bind((host, port))

