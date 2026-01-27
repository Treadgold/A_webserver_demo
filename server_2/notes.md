# ASYNCIO

How we serve many clients at once using asyncio event loops and coroutines.

The main idea is that instead of blocking on one operation (like accept() or recv()), we yield control back to the event loop, which can then run other tasks while we wait.

Helpfully, asyncio provides abstractions over sockets that let us use async/await syntax instead of dealing with low-level socket operations directly.

The main construct we are going to talk about is the asyncio.start_server() function, which creates a TCP server that can handle multiple clients concurrently.

asyncio.start_server is our entry point for creating an asynchronous TCP server. It binds to a host and port and listens for incoming connections. Each connection is handled asynchronously via the callback we provide. In our case, the handle_client function.

When a client connects, asyncio calls our handle_client coroutine, passing in reader and writer objects. These objects are high-level abstractions over the socket that let us read from and write to the connection asynchronously.

Instead of using our socket directly, we use await reader.read() to read data and writer.write() to send data. These calls yield control back to the event loop while waiting for I/O, allowing other tasks to run in the meantime.

Finally, we close the connection with writer.close() and await writer.wait_closed() to ensure all data is sent before closing.

It's a little tricky to visualise at first, because the thing are doing while waiting is actually doing exactly the same thing but for other clients! So the same handle_client function is being run for multiple clients at once, each one pausing at await points to let others run.

So before we go to far, lets set up our asyncio server so its ready to start its event loop and accept connections.

```python
import asyncio 

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    # Handle client connection
    pass  # We'll fill this in later

async def main():
    server = await asyncio.start_server(handle_client, '127.0.0.1', 8002)
    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    asyncio.run(main())

```

This code sets up an asyncio TCP server that listens on localhost:8002 and uses the handle_client coroutine to handle each incoming connection. That's all we need to replace sockets! Next, we need to implement the handle_client function to read requests and send responses, similar to what we did in the blocking server.

```python
async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    # Read data from the client
    data = await reader.read(1024)
    print(f"Received: {data.decode()}")

    # Send data to the client
    writer.write(b"Hello, Client!")
    await writer.drain()  # Ensure data is sent

    # Close the connection
    writer.close()
    await writer.wait_closed()
``` 

So lets compare this to our blocking server which uses socket.

In this version, instead of blocking on recv() and sendall(), we use await reader.read() and writer.write() with await writer.drain(). These calls yield control back to the event loop while waiting for I/O, allowing other client connections to be handled concurrently.

The await command is what makes this code asynchronous. When we hit an await, the coroutine pauses, and the event loop can run other tasks (like handling other clients) until the awaited operation completes.

Rather than go into a full explanation of ```async def``` and ```await``, I will provide an analogy, and simply note that the asyncio library already gives us some excellent abstractions on top of Python's async functions.


# Async vs Blocking — The Waiter Analogy

Imagine a restaurant with a single waiter. In a traditional, blocking server scenario, the waiter behaves like this:

 - The waiter approaches a table and takes an order.

 - He must stay at that table until the order is fully processed: the kitchen prepares the food, he goes to pick it up, and then finally delivers it back to the table.

 - Only after completing everything for that table can he move on to the next table.

The problem is obvious: if the kitchen takes a long time, all the other customers have to wait, because the waiter is stuck at one table. This is exactly what happens in a traditional blocking server — each request must complete fully before the server can start handling the next one.

Now, imagine the waiter is working in async mode, like our asyncio server:

 - The waiter approaches a table and takes the order.

 - Instead of waiting for the kitchen to prepare the food, he hands the order to the kitchen and immediately moves on to another table.

 - At another table, he might deliver food that’s ready, clear a finished plate, or take a new order.

Each time he completes a task, he scans the restaurant for needs and decides which is the next available task to complete; Clear plates, fill wine, seat new customer....etc.

Even though there’s still only one waiter, he can effectively manage 10 tables at once (or more, depending on how efficiently he moves between tasks). From the customers’ perspective, the restaurant feels responsive: orders are taken quickly, food arrives promptly, and plates are cleared regularly.

In the server world:

 - The waiter = the event loop
 - Each table = a client connection
 - Each task (take order, deliver food, clear plate) = a coroutine like handle_client
 - Yielding control with await allows the main event loop to run checks on which tasks are completed. It then grabs the next task, executes the next quick step, and passes results or inputs as needed, before going back to the loop to check again.


# Final thoughts

In reality, asyncio is even more powerful than what we’ve explored here. Beyond just managing many coroutines in a single thread, it can be combined with clever tools that are thread- and multiprocessor-aware, letting you take full advantage of modern hardware. This means you can run CPU-intensive tasks or blocking operations in separate threads or processes without having to wrestle with the low-level complexities of the threading or multiprocessing libraries yourself. Essentially, asyncio abstracts away much of the tricky coordination, so you can write clean, fast, and highly responsive code that scales efficiently.

Some of the cool things you can do with asyncio in real-world applications include:

 - Running network servers that handle thousands of concurrent connections with minimal overhead
 - Offloading blocking or CPU-bound tasks to separate threads or process pools seamlessly
 - Coordinating multiple I/O sources like files, sockets, or subprocesses without complex callbacks
 - Scheduling periodic tasks or timeouts in a precise, non-blocking way
 - Integrating with other async libraries, like aiohttp for web servers or aiomysql for database access
 - Building highly responsive GUIs or real-time applications where you don’t want the interface to freeze

If you keep exploring it, you’ll see how asyncio makes building real-world, high-performance Python applications much simpler — and honestly, kind of fun.