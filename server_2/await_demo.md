# 🔄 Understanding `async`/`await` Without `asyncio`

A hands-on guide to understanding Python's asynchronous primitives by building a minimal event loop from scratch.

---

## 🎯 Overview

This guide demonstrates how `async def` and `await` work at a fundamental level by implementing a simple event loop without relying on `asyncio` or any external libraries. By building the core components yourself, you'll gain a deep understanding of what happens under the hood when you write asynchronous Python code.

---

## 🧩 What This Code Does

### 🟦 The `Sleep` Class

The `Sleep` class is our custom awaitable object:

- **Implements `__await__()`** – This special method makes the object awaitable, allowing it to be used with the `await` keyword
- **Yields control** – When awaited, it yields itself back to the event loop, signaling "this coroutine needs to pause"
- **Tracks resume time** – The `resume_at` timestamp tells the loop exactly when this coroutine should wake up and continue execution

```python
class Sleep:
    def __init__(self, delay: float) -> None:
        self.delay: float = delay
        self.resume_at: float = time.monotonic() + delay
    
    def __await__(self) -> Iterator[None]:
        # Yield control back to the event loop
        yield self
        return None
```

### 🟧 The `EventLoop` Class

`EventLoop` is the core scheduler that orchestrates task execution:

**It maintains two key data structures:**

1. **`tasks`** – Coroutines that are ready to run immediately
2. **`sleeping`** – Awaitables that are paused, waiting for their time

**On each iteration, the loop:**

1. Checks the current time using `time.monotonic()`
2. Identifies and resumes any sleepers whose `resume_at` time has arrived
3. Advances each ready task by one step using `next()`
4. If a task yields a `Sleep` object, moves it to the `sleeping` list
5. If a task raises `StopIteration` (finished), removes it from the schedule

This models the fundamental responsibility of any event loop: **deciding who runs and when**.

```python
class EventLoop:
    def __init__(self) -> None:
        self.tasks: List[Iterator[None]] = []
        self.sleeping: List[Sleep] = []
    
    def create_task(self, coro) -> None:
        """Schedule a coroutine to run."""
        self.tasks.append(coro.__await__())
    
    def run(self) -> None:
        """Main event loop - runs until all tasks complete."""
        while self.tasks or self.sleeping:
            now: float = time.monotonic()
            
            # Resume any sleeps that are ready
            ready: List[Sleep] = [
                s for s in self.sleeping if s.resume_at <= now
            ]
            for sleep in ready:
                self.sleeping.remove(sleep)
                self.tasks.append(sleep.task)
            
            # Run one step of each task
            for task in list(self.tasks):
                try:
                    awaited = next(task)
                    if isinstance(awaited, Sleep):
                        awaited.task = task
                        self.sleeping.append(awaited)
                        self.tasks.remove(task)
                except StopIteration:
                    self.tasks.remove(task)
            
            time.sleep(0.01)  # Prevent busy-waiting
```

### 🟨 Coroutines in Action

Each call to `loop.create_task()` schedules a coroutine for execution:

```python
loop.create_task(my_task(4))
```

Inside the coroutine, this line pauses execution:

```python
await Sleep(t)
```

The `await` keyword does several things:

1. Calls `Sleep.__await__()` to get an iterator
2. Gets the next value from that iterator (which yields the `Sleep` object)
3. Passes control back to the event loop
4. The loop schedules resumption at the appropriate time

This is conceptually identical to what `await asyncio.sleep()` does in production code—the coroutine voluntarily yields control, allowing other tasks to run concurrently.

---

## 📋 Complete Example

Here's the full implementation demonstrating cooperative multitasking:

```python
from typing import List, Iterator
import time


class Sleep:
    """Custom awaitable that pauses a coroutine for a specified duration."""
    
    def __init__(self, delay: float) -> None:
        self.delay: float = delay
        self.resume_at: float = time.monotonic() + delay
    
    def __await__(self) -> Iterator[None]:
        # Yield control back to the event loop
        yield self
        return None


class EventLoop:
    """Minimal event loop that schedules and runs coroutines."""
    
    def __init__(self) -> None:
        self.tasks: List[Iterator[None]] = []
        self.sleeping: List[Sleep] = []
    
    def create_task(self, coro) -> None:
        """Add a coroutine to the task queue."""
        self.tasks.append(coro.__await__())
    
    def run(self) -> None:
        """Run the event loop until all tasks complete."""
        while self.tasks or self.sleeping:
            now: float = time.monotonic()
            
            # Wake up tasks whose sleep duration has elapsed
            ready: List[Sleep] = [
                s for s in self.sleeping if s.resume_at <= now
            ]
            for sleep in ready:
                self.sleeping.remove(sleep)
                self.tasks.append(sleep.task)
            
            # Execute one step of each ready task
            for task in list(self.tasks):
                try:
                    awaited = next(task)
                    if isinstance(awaited, Sleep):
                        awaited.task = task
                        self.sleeping.append(awaited)
                        self.tasks.remove(task)
                except StopIteration:
                    # Task completed
                    self.tasks.remove(task)
            
            time.sleep(0.01)  # Avoid busy-spinning


async def my_task(t: float) -> None:
    """Example coroutine that sleeps for a specified duration."""
    print(f"Task start for sleep {t}")
    await Sleep(t)
    print(f"Task resumed after sleep {t}")


# Create and run the event loop
loop = EventLoop()
loop.create_task(my_task(4))
loop.create_task(my_task(2))
loop.create_task(my_task(9))
loop.create_task(my_task(11))
loop.run()
```

**Expected Output:**

```
Task start for sleep 4
Task start for sleep 2
Task start for sleep 9
Task start for sleep 11
Task resumed after sleep 2
Task resumed after sleep 4
Task resumed after sleep 9
Task resumed after sleep 11
```

Notice how the tasks complete in order of their sleep duration, not the order they were scheduled—this demonstrates **cooperative multitasking** in action!

---

## 🌐 How This Mirrors Python's Real Event Loop

Python's built-in `asyncio` event loop performs similar orchestration, but with production-grade features:

| **Feature** | **Our Simple Loop** | **Real `asyncio`** |
|-------------|---------------------|-------------------|
| **Task Scheduling** | Based on sleep timers | Based on I/O readiness, timers, and futures |
| **I/O Handling** | None | Uses `select()`, `epoll`, or `kqueue` for efficient I/O multiplexing |
| **Concurrency** | Cooperative (via `await`) | Cooperative (via `await`) with thread-safe primitives |
| **Error Handling** | Minimal | Comprehensive exception handling and task cancellation |
| **Performance** | Educational | Highly optimized C implementations |

Your minimal `EventLoop` is a **pedagogical model** that captures the essence of asynchronous execution without the complexity of production systems.

---

## 🧭 Learning Resources

### 📚 Official Python Documentation

- **[Coroutines and Tasks](https://docs.python.org/3/library/asyncio-task.html)**  
  Comprehensive guide to how coroutines and Tasks behave in `asyncio`

- **[Event Loop Conceptual Overview](https://docs.python.org/3/howto/a-conceptual-overview-of-asyncio.html)**  
  Explains the event loop, coroutines, and awaitables in depth

### 🎓 Tutorials & Articles

- **[Async IO in Python: A Complete Walkthrough](https://realpython.com/async-io-python/)**  
  Excellent introductory tutorial covering `async`/`await` fundamentals

- **[Creating Custom Awaitables](https://superfastpython.com/asyncio-custom-awaitable-with-__await__/)**  
  Deep dive into implementing awaitables with `__await__()`

### 🔬 Advanced Topics

- **[PEP 492 – Coroutines with async and await syntax](https://peps.python.org/pep-0492/)**  
  The original proposal that introduced `async`/`await` to Python

- **[How the Python asyncio Event Loop Works](https://www.youtube.com/results?search_query=python+asyncio+internals)**  
  Video presentations on asyncio internals

---

## 🧠 Key Takeaways

### ✅ What We Learned

- **`async def`** creates a coroutine function—calling it returns a coroutine object, not an immediate result
- **`await`** yields control to the event loop, enabling cooperative multitasking
- **Event loops** schedule tasks, track their state, and resume them when ready
- **Awaitables** implement `__await__()` to define custom pause/resume behavior

### ⚠️ Limitations of This Implementation

This is an educational example, not production code. It lacks:

- Real I/O handling (network sockets, file operations)
- Task cancellation mechanisms
- Exception propagation and error handling
- Integration with OS-level event notification (epoll, kqueue)
- Callback scheduling and futures
- Thread safety and multiprocessing support

### 🚀 Next Steps

To continue your async Python journey:

1. Experiment with modifying the event loop (add priority scheduling, task cancellation, etc.)
2. Study how `asyncio` implements similar concepts with production features
3. Build simple async applications using real `asyncio`
4. Explore async libraries like `aiohttp`, `asyncpg`, or `trio`

---

## 💡 Final Thoughts

Understanding how `async`/`await` works at this fundamental level demystifies asynchronous programming. While production code uses `asyncio`'s robust event loop, the core concepts remain the same: **coroutines voluntarily yield control, and an event loop decides who runs next**.

This knowledge will make you a more effective async programmer, helping you debug issues, optimize performance, and write cleaner concurrent code.

Happy async coding! 🐍✨