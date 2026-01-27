from typing import List, Iterator
import time

class Sleep:
    def __init__(self, delay: float) -> None:
        
        self.delay: float = delay
        self.resume_at: float = time.monotonic() + delay

    def __await__(self) -> Iterator[None]:
        # Yield control back to the event loop
        yield self
        return None


class EventLoop:
    def __init__(self) -> None:
        self.tasks: List[Iterator[None]] = []
        self.sleeping: List[Sleep] = []

    def create_task(self, coro) -> None:
        self.tasks.append(coro.__await__())

    def run(self) -> None:
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

            time.sleep(0.01)  # avoid busy spin
            
            
async def my_task(t) -> None:
    print(f"Task start for sleep {t}")
    await Sleep(t)
    print(f"Task resumed after sleep {t}")
    
loop = EventLoop()

loop.create_task(my_task(4))
loop.create_task(my_task(2))
loop.create_task(my_task(9))
loop.create_task(my_task(11))

loop.run()