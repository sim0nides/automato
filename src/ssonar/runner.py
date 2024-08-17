import queue
import time
from abc import ABC, abstractmethod
from threading import Thread
from typing import Generic, TypeVar

SLEEP_STEP = 0.1


class BaseRunner(ABC):
    def __init__(self, delay_sec: float) -> None:
        self._run = False

        if delay_sec < 0:
            raise ValueError("Min delay_sec value is 0")

        self.delay_sec = delay_sec

    @property
    def is_running(self) -> bool:
        return self._run

    @abstractmethod
    def job(self) -> None:
        pass

    def __sleep(self, execution_time: float) -> None:
        sleep_time = self.delay_sec - execution_time

        while self._run and sleep_time > 0:
            time.sleep(SLEEP_STEP)
            sleep_time -= SLEEP_STEP

    def start(self) -> None:
        self._run = True

        while self._run:
            start_time = time.perf_counter()

            try:
                self.job()
            except Exception as e:
                print(e)

            exec_time = time.perf_counter() - start_time
            self.__sleep(exec_time)

    def stop(self) -> None:
        self._run = False


Task = TypeVar("Task")

_stop_signal = object()


class BaseRunnerWithConsumer(BaseRunner, Generic[Task]):
    def __init__(self, delay_sec: float) -> None:
        super().__init__(delay_sec)
        self._queue: queue.Queue[Task] = queue.Queue()

    @abstractmethod
    def task(self, task: Task) -> None:
        """Process task from queue"""
        pass

    def _consumer(self) -> None:
        while self._run:
            try:
                task = self._queue.get(timeout=0.1)

                if task is _stop_signal:
                    self._queue.task_done()
                    break

                self.task(task)
                self._queue.task_done()
            except queue.Empty:
                pass
            except Exception as e:
                print(e)

    def put_to_queue(self, task: Task) -> None:
        self._queue.put(task)

    def start(self) -> None:
        t = Thread(target=self._consumer)
        t.start()
        super().start()
        t.join()

    def stop(self) -> None:
        super().stop()
        self._queue.put(_stop_signal)
