import logging
import queue
import signal
import time
from functools import cached_property
from threading import Lock, Thread
from typing import Callable, Generic, TypeVar

from automato.logging import create_logger

_SLEEP_STEP = 0.1
_DEFAULT_DELAY_SEC = 10

_T = TypeVar("_T")
_JobFunc = Callable[[], None]
_TaskFunc = Callable[[_T], None]


class Automato:
    _run: bool = False
    _job: _JobFunc | None = None

    def __init__(
        self, delay_sec: float = _DEFAULT_DELAY_SEC, debug: bool | None = False
    ) -> None:
        if delay_sec < 0:
            raise ValueError("Min delay_sec value is 0")

        self._delay_sec: float = delay_sec
        self._debug: bool | None = debug

        signal.signal(signal.SIGTERM, self._handle_signal)
        signal.signal(signal.SIGINT, self._handle_signal)

    @cached_property
    def logger(self) -> logging.Logger:
        return create_logger(self._debug)

    @property
    def is_running(self) -> bool:
        return self._run

    def job(self, func: _JobFunc):
        """Decorator to register job function"""
        self._job = func

    def _handle_signal(self, *args) -> None:
        self.stop()

    def _sleep(self, execution_time: float) -> None:
        sleep_time = self._delay_sec - execution_time

        while self.is_running and sleep_time > 0:
            time.sleep(_SLEEP_STEP)
            sleep_time -= _SLEEP_STEP

    def _handle_job(self) -> None:
        self._job()  # type: ignore

    def start(self) -> None:
        self.logger.info("Start")

        if self._job is None:
            raise ValueError("Job is not registered")

        self._run = True

        while self.is_running:
            start_time = time.perf_counter()

            try:
                self._handle_job()
            except Exception:
                self.logger.exception("Job failed")

            exec_time = time.perf_counter() - start_time
            self._sleep(exec_time)

    def stop(self) -> None:
        self.logger.info("Stop")
        self._run = False


class AutomatoWithTasks(Automato, Generic[_T]):
    _stop_signal = object()

    _lock: Lock = Lock()

    _task: _TaskFunc[_T] | None = None

    _queue: queue.Queue[_T | object] = queue.Queue()

    @property
    def lock(self):
        return self._lock

    def task(self, func: _TaskFunc[_T]) -> None:
        """Decorator to register task function"""
        self._task = func

    def _consumer(self) -> None:
        while True:
            try:
                task = self._queue.get(timeout=0.1)

                if task is AutomatoWithTasks._stop_signal:
                    self._queue.task_done()
                    break

                self._task(task)  # type: ignore
                self._queue.task_done()
            except queue.Empty:
                pass
            except Exception:
                self.logger.exception("Unexpected error in consumer")

    def to_consumer(self, task: _T) -> None:
        self._queue.put(task)

    def start(self) -> None:
        if self._task is None:
            raise ValueError("Consumer is not registered")

        t = Thread(target=self._consumer)
        t.start()
        super().start()
        t.join()

    def stop(self) -> None:
        super().stop()
        self._queue.put(AutomatoWithTasks._stop_signal)
