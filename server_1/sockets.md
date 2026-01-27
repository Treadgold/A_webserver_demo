# What is a Socket ?
A socket is an endpoint for sending or receiving data across a computer network. It is a software abstraction that allows communication between different processes, either on the same machine or across different machines over a network.

# Socket Types
### Socket Address Families

| Address Family  |What it connects |
|----------------|------------------|
| AF_INET |IPv4 (IP + port) |
| AF_INET6 |IPv6 |
| AF_UNIX |Local machine only  (filesystem path or abstract name) |
| AF_BLUETOOTH |Bluetooth |
| AF_NETLINK |Kernel ↔ user space  (Linux) |
| AF_VSOCK |Host ↔ virtual machines |

 - IP addresses are not inherent to sockets
 - They’re inherent to Internet address families

### There are several layers of communication that matter here:

```
Your Python code
↓
Socket API (send, recv)
↓
Transport protocol (TCP / UDP / others)
↓
Network / link layer (IP, Bluetooth, Ethernet, Wi-Fi)
↓
Physical medium (copper, radio, fibre)
```

When we create a socket, we specify:

- The socket type (e.g., stream or datagram)
- The address family (e.g., IPv4, IPv6, Unix domain)
- The transport protocol (e.g., TCP, UDP, usually implied by the socket type)

The physical medium and link layer are abstracted away by the operating system and network stack.


# Creating a Socket

In Python, you can create a socket using the `socket` module.

## TCP Sockets

Here's an example of creating a TCP socket using the IPv4 address family:

```python
import socket

# Define the endpoint parameters 
host = 'localhost'
port = 8080

# Create a TCP socket using IPv4
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# now we can bind to the endpoint
sock.bind((host, port))
```

Binding to localhost only accepts connections from the same machine, typically binding to 127.0.0.1; 0.0.0.0 listens on all IPv4 interfaces.

I have deliberately used localhost in all my examples to avoid security issues. Never bind a server to 0.0.0.0 on a machine connected to the internet unless you are absolutely sure you know what you are doing.

It bears mentioning that on a windows machine:
 - Windows Defender Firewall prompts or blocks by default for inbound connections
 - The first bind/listen may succeed, but traffic is dropped
 - Users often see a firewall popup on first run

On Linux and MacOS usually allow binding to any port above 1024 without special permissions, though firewall rules may still block traffic.

## What about UDP Sockets?

We could also create a UDP socket like this:

```python
import socket

# define the endpoint parameters
host = 'localhost'
port = 8080

# Create a UDP socket using IPv4
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((host, port))
```

You've all seen an IP address before, a port is just a number that lets the operating system route incoming data to the correct process on a machine.

Notice we still use the same address family ( AF_INET ) but change the socket type from SOCK_STREAM to SOCK_DGRAM.

UDP (SOCK_DGRAM) is:

 - Connectionless
 - Unreliable
 - Message-based (datagrams)
 - Fast, low overhead

What this means in code:

 - One sendto() → one packet
 - One recvfrom() → one packet
 - Packet may be lost or duplicated!

Used for:

 - DNS
 - Games
 - Audio/video streaming
 - Discovery protocols

### Important mental shift:

UDP is not “worse TCP” — it’s...

“you are the reliability layer now”.


# Now how do we use the socket?

Well, we create the socket, bind it to an endpoint, and then we can send packets, but first we need to listen for incoming connections (for TCP):

```python
# Listen for incoming connections
sock.listen(5)
print(f"Server listening on {host}:{port}")

# Accept a connection
client_socket, client_address = sock.accept()

print(f"Connection from {client_address} has been established!")

```

### IMPORTANT
The accept() call is blocking — it will wait here until a client connects.

That print statement will only execute once a client has connected. If no-one tries to connect, the server will just sit there waiting on the sock.accept() line.

In synchronous code, every blocking call stops the entire program. Async frameworks like asyncio exist to let us wait on many sockets at once.

### Notice We haven't used the ```with``` statement to open the socket here.

This is because we want the socket to stay open for the lifetime of the server process. If we used ```with```, the socket would automatically close as soon as we exited the ```with``` block. We could put all our code inside the ```with``` block, but that would be less clear. Usually we want to do a bit of work while the socket is open, so we just manage the socket's lifetime manually.

# Sending and Receiving Data

Once a connection is accepted, we can send and receive data using the client_socket object:

```python
# Receive data from the client
data = client_socket.recv(1024)
print(f"Received: {data.decode()}")
# Send data to the client
client_socket.sendall(b"Hello, Client!")
```

__NB: A web browser is just a TCP client that connects to a server, sends text, and waits for a response.__

Notice how we requested a specific number of bytes (1024) in the recv() call. TCP is a stream protocol, so we need to manage message boundaries ourselves.

If our message is larger than 1024 bytes, we may need to call recv() multiple times to get the full message.

A simple way to check if there is any more data to read is to keep calling recv() until it returns an empty byte string (b''), which indicates the client has closed the connection.

In our example, we just read once for simplicity. 1024 bytes is usually enough for small messages, like a browser requesting a web page.

Finally, we should close the sockets when we're done:

```python
# Close the client socket
client_socket.close()
# Close the server socket
sock.close()
```

# Why Python's sockets feel "low-level"

Simply put, Because it is.

Python’s socket module is:

 - A near-direct wrapper over BSD sockets
 - Intentionally minimal
 - Almost hostile to beginners 😄

Higher-level libraries build on it:

 - http.client
 - urllib
 - asyncio
 - requests
 - aiohttp
 - socketserver

Understanding raw sockets makes all of these feel obvious instead of magical.

# The minimal conceptual model 
### This is the core


Every socket has four defining choices:

 - Address family
    - Internet?
    - Unix?
    - Bluetooth?

 - Transport type
     - Stream (TCP-like)
     - Datagram (UDP-like)

 - Protocol
    - Usually 0 (default for the family)
    - Sometimes explicit (e.g. Bluetooth RFCOMM)

 - Role
    - Server (bind + listen + accept)
    - Client (connect)

Everything else is mechanics.