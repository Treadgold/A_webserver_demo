# Educational HTTP Servers in Python

> **⚠️ WARNING: NOT FOR PRODUCTION USE**
>
> These servers are educational tools designed to teach HTTP server fundamentals. They lack essential security features, error handling, and performance optimizations required for production environments. Never deploy these servers in production or expose them to the public internet.

## Overview

This project demonstrates how to build HTTP servers in Python, progressing from a simple blocking server to an asynchronous server with routing capabilities. Each implementation builds upon the previous one, illustrating core web server concepts using only Python's standard library.

**Learning Path:**
1. **Blocking Server** - The simplest possible HTTP server
2. **Async Server** - Adding non-blocking I/O for better performance
3. **Routing Server** - Introducing route handlers like modern frameworks

## Project Structure

```
.
├── blocking_server.py    # Step 1: Synchronous blocking server
├── async_server.py        # Step 2: Asynchronous server
├── routing_server.py      # Step 3: Server with routing decorators
└── static/                # Static files served by all servers
    ├── index.html
    ├── about.html
    ├── complex.html
    ├── help.html
    ├── styles.css
    └── styles2.css
```

## Prerequisites

- Python 3.7 or higher (for `asyncio` support)
- Basic understanding of Python syntax
- No external dependencies required (standard library only)

## Running the Servers

Each server runs on `http://127.0.0.1:8002`:

```bash
# Run the blocking server
python blocking_server.py

# Run the async server
python async_server.py

# Run the routing server
python routing_server.py
```

Press `Ctrl+C` to stop any server.

---

## Part 1: Blocking Server (`blocking_server.py`)

The blocking server is the foundation - it handles one request at a time, waiting for each to complete before accepting the next.

### Key Concepts

#### What is a Socket?

A **socket** is the fundamental building block of network communication. Think of it as a two-way communication endpoint - like a telephone connection between your computer and another computer. Just as you need a phone number to call someone, sockets use IP addresses and port numbers to establish connections.

The `socket` module from Python's standard library provides the low-level networking interface. When you visit a website in your browser, your browser creates a socket to connect to the web server's socket. Data flows in both directions through this connection.

```python
import socket
```

**Why we need sockets:** Without sockets, computers couldn't communicate over networks. Every network application - web browsers, email clients, chat apps, online games - uses sockets under the hood.

#### Creating the Server Socket

A server socket is like setting up a receptionist at a front desk - it waits for incoming connections and handles them.

```python
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("127.0.0.1", 8002))
server_socket.listen(5)
```

Let's break down each part:

- `socket.AF_INET` - Use IPv4 addresses (the standard format like `192.168.1.1`)
- `socket.SOCK_STREAM` - Use TCP protocol (reliable, ordered data transmission where packets arrive in the correct sequence)
- `bind(("127.0.0.1", 8002))` - Attach to IP address `127.0.0.1` (localhost, meaning this computer) and port `8002`
- `listen(5)` - Allow up to 5 pending connections in the queue waiting to be accepted

**What is localhost (127.0.0.1)?** This is a special IP address that always refers to "this computer." It's used for testing and development so your server only accepts connections from your own machine, not from the internet.

**What is a port?** A single computer can run many network services simultaneously (web server, email server, database, etc.). Ports are like apartment numbers - they let the computer know which service should receive the incoming connection. Port 8002 is arbitrary; we could use 8000, 3000, or any unused port above 1024.

#### The Main Server Loop

```python
while True:
    client_socket, addr = server_socket.accept()  # Wait for a connection
    handle_client(client_socket)                   # Process the request
```

**This is "blocking"** - `accept()` pauses execution until a client connects. While handling one request, new requests must wait.

#### Receiving HTTP Requests

When a browser connects to our server, it sends a text message following the HTTP protocol - a standardized format that all web servers and browsers understand.

```python
request_bytes = client_socket.recv(1024)  # Read up to 1024 bytes
request = request_bytes.decode("utf-8")    # Convert bytes to string
```

**Why bytes?** Network communication happens in **bytes** (raw binary data), not strings. The `recv(1024)` method reads up to 1024 bytes from the socket. We then decode these bytes into a human-readable string using UTF-8 encoding.

An actual HTTP request from a browser looks like this:

```
GET /index.html HTTP/1.1
Host: 127.0.0.1:8002
User-Agent: Mozilla/5.0
Accept: text/html
...
```

The first line is the most important - it tells us:
- **Method** (`GET`) - What action to perform (GET = retrieve a resource)
- **Path** (`/index.html`) - What resource is being requested
- **Protocol** (`HTTP/1.1`) - Which version of HTTP to use

The following lines are **headers** - additional metadata about the request, like which browser is making the request, what types of content it accepts, etc.

#### Parsing the Request Path

```python
def parse_http_path(request: str) -> str:
    first_line = request.splitlines()[0]  # "GET /index.html HTTP/1.1"
    _, path, _ = first_line.split()       # Extract middle part
    return path                            # Returns "/index.html"
```

#### Resolving File Paths

```python
def resolve_request_path(request_path: str) -> Path:
    if request_path == "/":
        request_path = "/index.html"  # Default page
    elif not Path(request_path).suffix:
        request_path += ".html"        # Add .html to extensionless paths
    
    return STATIC_DIR / request_path.lstrip("/")
```

**The `pathlib` module** provides `Path` objects for working with file paths in a cross-platform way.

#### Determining Content Type

Modern web browsers are **strict** about knowing what type of content they're receiving. When you send a file to a browser, you must tell it whether it's HTML to render, CSS to apply as styles, JavaScript to execute, or an image to display. This information is communicated through the **Content-Type header** in the HTTP response.

```python
MIME_TYPES = {
    ".html": "text/html",
    ".css": "text/css",
    ".js": "application/javascript",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".svg": "image/svg+xml",
}

def get_content_type(file_path: Path) -> str:
    extension = file_path.suffix.lower()  # Get file extension
    return MIME_TYPES.get(extension, "application/octet-stream")
```

**What are MIME types?** MIME (Multipurpose Internet Mail Extensions) types are standardized labels that identify file formats. The format is always `type/subtype`, like `text/html` or `image/png`.

**Why this matters:** Without the correct Content-Type header, browsers won't know how to handle the file:
- **CSS files without `text/css`** → Styles won't be applied to your page
- **JavaScript without `application/javascript`** → Code won't execute
- **Images without proper type** → May not display at all
- **HTML without `text/html`** → Might be downloaded instead of rendered

The browser uses the Content-Type header (not the file extension) to make these decisions. Even if your file is named `styles.css`, if you send it with `Content-Type: text/plain`, the browser will treat it as plain text and ignore all the styling rules.

#### Building the HTTP Response

An HTTP response is a carefully formatted text message that the browser knows how to interpret. It consists of a status line, headers, and the actual content.

```python
def http_response(body: bytes, status: str = "200 OK", 
                  content_type: str = "text/html") -> bytes:
    headers = (
        f"HTTP/1.1 {status}\r\n"
        f"Content-Type: {content_type}\r\n"
        f"Content-Length: {len(body)}\r\n"
        "\r\n"  # Blank line separates headers from body
    )
    return headers.encode("utf-8") + body
```

**Understanding the response structure:**

An HTTP response has two main parts:
1. **Headers** - Metadata about the response (what kind of data, how much, etc.)
2. **Body** - The actual content (HTML, CSS, image data, etc.)

**Line endings matter!** HTTP requires `\r\n` (carriage return + line feed) at the end of each line. This is a historical convention from old teletype machines. Using just `\n` won't work properly.

**Status codes** tell the browser what happened:
- `200 OK` - Success! Here's what you asked for
- `404 Not Found` - That file doesn't exist
- `500 Internal Server Error` - Something broke on the server
- `301 Moved Permanently` - The resource moved to a new URL

**Content-Length** is critical - it tells the browser how many bytes of content to expect. Without it, the browser might wait indefinitely or cut off data prematurely.

The **blank line** (`\r\n\r\n`) between headers and body is mandatory. This is how the browser knows "headers are done, content starts now."

#### Sending the Response

Once we've built our HTTP response, we need to send it back to the browser through the socket connection.

```python
client_socket.sendall(response)  # Send all bytes
client_socket.close()             # Close the connection
```

**Why `sendall()` instead of `send()`?** The `send()` method might not send all your data in one go - it returns how many bytes were actually sent. The `sendall()` method keeps sending until all data is transmitted or an error occurs. This ensures the browser receives the complete response.

**Why close the connection?** HTTP/1.1 can support persistent connections, but for simplicity, we close after each request. This tells the browser "the response is complete" and frees up system resources. The socket is a finite resource - if we never close connections, we'll eventually run out.

### Limitations of Blocking Servers

- **One request at a time** - While serving one client, others must wait
- **Slow under load** - 100 simultaneous users = 99 waiting users
- **Wastes CPU time** - The server sits idle while waiting for I/O

---

## Part 2: Async Server (`async_server.py`)

The async server uses **asyncio** to handle multiple requests concurrently without threading or multiprocessing.

### Key Concepts

#### What is asyncio?

**asyncio** is Python's built-in library for writing asynchronous code. "Asynchronous" means "not happening at the same time" - but in programming, it specifically means we can start multiple operations and switch between them while waiting for results, rather than blocking and doing nothing.

```python
import asyncio
```

**The problem asyncio solves:** Traditional synchronous code waits idly during I/O operations. When you read from a network socket, your program literally does nothing while waiting for data to arrive - maybe for milliseconds, maybe seconds. This is wasteful, especially for servers handling many connections.

**Real-world analogy:** Imagine a chef (blocking) who starts cooking pasta, then stands motionless staring at the pot until the water boils, then stands motionless again while it cooks. An async chef starts the pasta, checks on it periodically while preparing other dishes, and handles multiple pots simultaneously. Same kitchen, same chef, much more efficient.

**asyncio doesn't use multiple threads or processes** - it's still a single thread making rapid context switches between tasks. This makes it lighter weight and avoids many concurrency pitfalls.

#### Async Functions

Async functions look similar to regular functions but behave very differently.

```python
async def handle_client(reader, writer):
    # This function can pause and let other tasks run
    request_bytes = await reader.read(1024)  # Pause here while reading
```

**Key syntax:**
- `async def` - Declares an asynchronous function (also called a "coroutine")
- `await` - Pauses execution of this function until the operation completes, allowing other tasks to run

**What actually happens with `await`?** When your code hits `await reader.read(1024)`, it tells asyncio: "I'm waiting for data from the network. While I wait, run other tasks that are ready to make progress." This is cooperative multitasking - each function voluntarily yields control.

**You can only use `await` inside `async def` functions.** This is a language rule. Regular functions can't use `await`, and async functions should generally `await` something (otherwise there's no benefit to making them async).

#### Creating the Async Server

```python
server = await asyncio.start_server(
    handle_client,      # Function to call for each connection
    host="127.0.0.1",
    port=8002,
)
```

**`asyncio.start_server()`** creates a server that automatically handles new connections concurrently. Each new connection gets its own call to `handle_client()`.

#### Async Streams (Reader and Writer)

Instead of raw sockets, asyncio provides a higher-level abstraction: **StreamReader** and **StreamWriter**. These wrap the low-level socket operations in an async-friendly interface.

```python
async def handle_client(reader: asyncio.StreamReader, 
                        writer: asyncio.StreamWriter):
    request_bytes = await reader.read(1024)    # Non-blocking read
    # ... process request ...
    writer.write(response)                      # Buffer the response
    await writer.drain()                        # Actually send it
    writer.close()                              # Close connection
```

**Understanding each operation:**

- **`reader.read(1024)`** - Asynchronously read up to 1024 bytes from the client. This returns a "future" (promise of data) that we `await`. While waiting for network data, other connections can be processed.

- **`writer.write(response)`** - Add data to an internal buffer. This doesn't actually send anything yet! It's like putting a letter in your outbox instead of walking to the mailbox.

- **`writer.drain()`** - Flush the buffer and send all queued data over the network. We `await` this because network sending can take time. The "drain" metaphor is like draining water from a tank - empty the buffer.

- **`writer.close()`** - Close the connection gracefully. This tells the client "no more data coming" and frees the socket resource.

**Why separate `write()` and `drain()`?** This allows buffering multiple writes together before actually sending, which is more efficient. You can call `write()` many times, then `drain()` once to send everything together.

#### Running the Server Forever

```python
async with server:
    await server.serve_forever()
```

This keeps the server running and accepting connections indefinitely.

#### The Event Loop

The event loop is the "conductor" of asyncio - it orchestrates all the async operations, decides which task to run next, and handles the switching between tasks.

```python
asyncio.run(main())
```

**`asyncio.run()`** does several things:
1. Creates a new event loop
2. Runs your async `main()` function in that loop
3. Manages all tasks spawned by your program
4. Cleans up and closes the loop when done

**What is an event loop?** Think of it as a super-fast task manager that constantly cycles through:
1. Check which tasks are waiting for I/O (network, disk, etc.)
2. See if any I/O has completed
3. Wake up tasks whose I/O is ready
4. Run those tasks until they hit another `await`
5. Repeat

This happens thousands of times per second. Each "lap" around the loop takes microseconds, creating the illusion that everything runs simultaneously, even though only one task executes at any given microsecond.

**Event loop vs threading:** With threads, the operating system decides when to switch between tasks (preemptive multitasking). With event loops, tasks explicitly yield control with `await` (cooperative multitasking). This makes async code more predictable and avoids many thread-safety issues.

### How Async Improves Performance

**Blocking server:**
```
Request 1: [Processing........] Done
Request 2:                      [Processing........] Done
Request 3:                                          [Processing........] Done
```

**Async server:**
```
Request 1: [Processing........] Done
Request 2: [Processing.....] Done
Request 3:   [Processing........] Done
```

All three requests can be processed concurrently!

### What Stays the Same?

The HTTP protocol logic is identical - we still need to:
- Parse the request path from the HTTP request line
- Resolve which file or resource is being requested
- Determine the correct MIME type for the response
- Build a properly formatted HTTP response with headers and body

**This is an important lesson:** The core concepts of HTTP don't change just because we're using async I/O. What changes is *how* we read from and write to the network - the *what* (HTTP protocol) remains constant. You could swap asyncio for threads, multiprocessing, or any other concurrency model and still use the exact same HTTP parsing and response building logic.

---

## Part 3: Routing Server (`routing_server.py`)

The routing server adds **route decorators**, similar to Flask or FastAPI, allowing you to map URL paths to specific handler functions.

### Key Concepts

#### What is Routing?

**Routing** maps URL paths to specific handler functions. Instead of just serving static files from disk, routing lets you execute custom Python code based on the requested URL.

Think of routing like a mail sorting facility - incoming requests (letters) get directed to the appropriate handler (department) based on their path (address).

**Examples of what routing enables:**

- `/` → Run `homepage()` function, which might fetch user data from a database and render a personalized page
- `/about` → Serve the static about.html file
- `/api/users` → Return JSON data of all users
- `/search?q=python` → Parse the query parameter and return search results
- `/blog/my-post-title` → Extract the post title, query database, render article

**Without routing:** You can only serve files that exist on disk. Every page needs a physical `.html` file.

**With routing:** You can generate content dynamically, interact with databases, process form submissions, and create RESTful APIs - all the things modern web applications do.

#### The Routes Dictionary

```python
routes = {}  # Maps paths to handler functions
```

This dictionary stores path-to-function mappings: `"/about"` → `about_page()`.

#### The Route Decorator

A **decorator** is a function that wraps another function to modify its behavior or register it somewhere. Python's `@` syntax is syntactic sugar that makes decorators clean to use.

```python
def route(path: str):
    def decorator(func):
        routes[path] = func  # Register the function
        return func
    return decorator
```

**How decorators work:**

When Python sees:
```python
@route("/about")
def about_page():
    return b"<h1>About</h1>"
```

It automatically executes:
```python
def about_page():
    return b"<h1>About</h1>"

about_page = route("/about")(about_page)
```

**Step-by-step breakdown:**
1. `route("/about")` is called, returning the inner `decorator` function
2. This `decorator` function receives `about_page` as an argument
3. Inside `decorator`, we register the path: `routes["/about"] = about_page`
4. The decorator returns the original function unchanged
5. The name `about_page` now refers to the decorated function (which is still the original function, but it's been registered in our `routes` dict)

**Why use decorators for routing?** It's a clean, readable syntax that keeps the route path visually close to the code that handles it. Compare:

```python
# With decorator
@route("/about")
def about_page():
    return b"..."

# Without decorator  
def about_page():
    return b"..."
routes["/about"] = about_page  # Easy to forget or get separated from function
```

#### Using the Decorator

```python
@route("/about")
def about_page() -> bytes:
    return load_static_file("about.html") or b"<h1>Missing about.html</h1>"

@route("/")
def index_route() -> bytes:
    return load_static_file("index.html") or b"<h1>Missing index.html</h1>"
```

The `@route("/about")` syntax is equivalent to:

```python
def about_page() -> bytes:
    return load_static_file("about.html") or b"<h1>Missing about.html</h1>"

about_page = route("/about")(about_page)
```

Now `routes` contains: `{"/about": about_page, "/": index_route}`

#### Handling Requests with Routes

```python
handler = routes.get(path)
if handler:
    body = handler()  # Call the registered function
    response = http_response(body, content_type="text/html")
else:
    # Fallback to serving static files
    body = load_static_file(path)
    # ...
```

**Request flow:**
1. Parse the requested path from HTTP request
2. Check if a route handler exists for that path
3. If yes → call the handler function
4. If no → try to serve a static file
5. If no file exists → return 404

#### Why Use Routing?

Routing enables:
- **Dynamic content** - Generate HTML based on database queries
- **API endpoints** - Return JSON data
- **Form handling** - Process POST requests
- **Custom logic** - Execute any Python code for specific URLs

Modern frameworks like **FastAPI** and **Flask** use this pattern extensively:

```python
# FastAPI example (similar concept)
@app.get("/users/{user_id}")
async def read_user(user_id: int):
    return {"user_id": user_id}
```

### Path Resolution with Security

```python
def load_static_file(path: str) -> Optional[bytes]:
    file_path = resolve_file_path(path)
    if not file_path.is_relative_to(STATIC_DIR.resolve()):
        return None  # Prevent directory traversal attacks
    # ...
```

**Security note:** The `is_relative_to()` check prevents malicious requests like `/../../etc/passwd` from accessing files outside the static directory. Production servers need many more security measures!

---

## Common Components Across All Servers

All three servers share the same fundamental HTTP logic. This demonstrates an important principle: **the protocol layer (HTTP) is independent of the I/O layer (blocking/async)**.

### MIME Types Dictionary

All three servers use the same MIME type mapping:

```python
MIME_TYPES = {
    ".html": "text/html",
    ".css": "text/css",
    ".js": "application/javascript",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".svg": "image/svg+xml",
}
```

This dictionary is consulted every time we serve a file to determine the correct `Content-Type` header. The mapping from file extension to MIME type is standardized - we can't just make up our own values. Browsers expect these exact strings.

**Why these specific values?** These MIME types are registered with IANA (Internet Assigned Numbers Authority), the organization that maintains internet standards. Using non-standard MIME types will confuse browsers.

### HTTP Response Format

All servers follow the HTTP/1.1 protocol specification (RFC 2616). Every response must have this exact structure:

```
HTTP/1.1 200 OK\r\n
Content-Type: text/html\r\n
Content-Length: 1234\r\n
\r\n
<html>...</html>
```

**The anatomy of an HTTP response:**

1. **Status line:** `HTTP/1.1 200 OK`
   - Protocol version (always `HTTP/1.1` in our case)
   - Status code (200 = success, 404 = not found, 500 = server error)
   - Reason phrase (human-readable description)

2. **Headers:** Key-value pairs separated by `: `
   - Each header ends with `\r\n`
   - Headers are case-insensitive (Content-Type = content-type = CONTENT-TYPE)
   - Common headers: Content-Type, Content-Length, Set-Cookie, Cache-Control

3. **Blank line:** `\r\n` (just a carriage return and line feed)
   - Mandatory separator between headers and body
   - Without this, the browser won't know where headers end

4. **Body:** Actual content (HTML, CSS, JSON, image bytes, etc.)
   - Length must match the Content-Length header
   - Encoding depends on Content-Type

**Why is the format so strict?** HTTP is a text-based protocol designed for reliable communication between different systems. A browser made by Apple needs to understand responses from a server running Linux, which might be serving content created on Windows. Strict formatting ensures interoperability.

### Error Handling

All servers return 404 responses for missing files:

```python
body = b"<h1>404 Not Found</h1>"
response = http_response(body, status="404 Not Found", content_type="text/html")
```

---

## Learning Exercises

### Beginner

1. **Add a new MIME type** - Support `.gif` images by adding to `MIME_TYPES`
2. **Create a new static page** - Add `contact.html` to the `static` folder
3. **Change the port** - Modify the port from `8002` to `8080`

### Intermediate

1. **Add request logging** - Print each requested path and timestamp
2. **Implement POST support** - Parse POST request bodies
3. **Add a custom route** - Create a route that returns the current time
4. **Query parameters** - Parse and use URL query strings (`?name=value`)

### Advanced

1. **Session support** - Implement cookie-based sessions
2. **Template rendering** - Add simple variable substitution in HTML
3. **JSON API endpoint** - Return JSON data with proper Content-Type
4. **Middleware system** - Add functions that run before/after route handlers
5. **WebSocket support** - Extend the async server with WebSocket connections

---

## Key Takeaways

### Blocking Server
- **Simplest to understand** - Sequential request handling
- **Easy to debug** - One request at a time
- **Poor scalability** - Can't handle concurrent users efficiently

### Async Server
- **Better performance** - Handle many connections simultaneously
- **Same protocol logic** - HTTP parsing/response building unchanged
- **More complex** - Requires understanding async/await

### Routing Server
- **Framework-like** - Resembles Flask, FastAPI, Django
- **Flexible** - Mix static files and dynamic routes
- **Extensible** - Easy to add new routes with decorators

### Why This Matters

These servers strip away framework magic to reveal:
- HTTP is just formatted text over TCP sockets
- Async is about efficient I/O, not threading
- Routing is just mapping paths to functions
- Web frameworks build on these fundamentals

---

## Further Reading

- [Python socket documentation](https://docs.python.org/3/library/socket.html)
- [Python asyncio documentation](https://docs.python.org/3/library/asyncio.html)
- [HTTP/1.1 specification (RFC 2616)](https://www.ietf.org/rfc/rfc2616.txt)
- [MIME types reference](https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types)

---

## License

This is educational code for learning purposes. Use at your own risk.

**Remember: Never use these servers in production!**