import time
from abc import ABC, abstractmethod

SLEEP_STEP = 0.1


class BaseRunner(ABC):
    def __init__(self, delay_sec: float) -> None:
        self.__run = False

        if delay_sec < 0:
            raise ValueError("Min delay_sec value is 0")

        self.delay_sec = delay_sec

    @property
    def is_running(self) -> bool:
        return self.__run

    @abstractmethod
    def job(self) -> None:
        pass

    def __sleep(self, execution_time: float) -> None:
        sleep_time = self.delay_sec - execution_time

        while self.__run and sleep_time > 0:
            time.sleep(SLEEP_STEP)
            sleep_time -= SLEEP_STEP

    def start(self) -> None:
        self.__run = True

        while self.__run:
            start_time = time.perf_counter()

            try:
                self.job()
            except Exception as e:
                print(e)

            exec_time = time.perf_counter() - start_time
            self.__sleep(exec_time)

    def stop(self) -> None:
        self.__run = False
