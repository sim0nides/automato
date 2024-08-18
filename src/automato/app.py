import queue
import signal
import time
from threading import Lock, Thread
from typing import Callable, Generic, TypeVar

_SLEEP_STEP = 0.1

_T = TypeVar("_T")
_JobFunc = Callable[[], _T]
_TaskFunc = Callable[[_T], None]


class Automato(Generic[_T]):
    def __init__(self, delay_sec: float) -> None:
        if delay_sec < 0:
            raise ValueError("Min delay_sec value is 0")

        self._run: bool = False
        self._delay_sec: float = delay_sec
        self._job: _JobFunc[_T] | None = None

        signal.signal(signal.SIGTERM, self._handle_signal)
        signal.signal(signal.SIGINT, self._handle_signal)

    @property
    def is_running(self) -> bool:
        return self._run

    def job(self, func: _JobFunc[_T]):
        """Decorator to register job function"""
        self._job = func

    def _handle_signal(self, *args) -> None:
        self.stop()

    def _sleep(self, execution_time: float) -> None:
        sleep_time = self._delay_sec - execution_time

        while self.is_running and sleep_time > 0:
            time.sleep(_SLEEP_STEP)
            sleep_time -= _SLEEP_STEP

    def _run_job(self) -> _T:
        return self._job()  # type: ignore

    def start(self) -> None:
        if self._job is None:
            raise ValueError("Job is not registered")

        self._run = True

        while self.is_running:
            start_time = time.perf_counter()

            try:
                self._run_job()
            except Exception as e:
                print(e)

            exec_time = time.perf_counter() - start_time
            self._sleep(exec_time)

    def stop(self) -> None:
        print("Stop")
        self._run = False


class AutomatoWithTasks(Automato[_T]):
    _stop_signal = object()

    def __init__(self, *args, **kw) -> None:
        super().__init__(*args, **kw)
        self._lock: Lock = Lock()
        self._queue: queue.Queue[_T | object] = queue.Queue()
        self._task: _TaskFunc[_T] | None = None

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
            except Exception as e:
                print(e)

    def _run_job(self):
        result = self._job()  # type: ignore
        self._put_to_queue(result)

    def _put_to_queue(self, task: _T) -> None:
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
