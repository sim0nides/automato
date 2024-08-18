import time

from automato.runner import RunnerWithTasks

runner = RunnerWithTasks[str](delay_sec=5)


@runner.job
def job():
    job_result = "job_result"
    print(f"Job: {job_result}")
    return job_result


@runner.task
def task(task: str):
    with runner.lock:
        print("sleeping...")
        time.sleep(2)
        print(f"Task: {task}")


def main():
    runner.start()


if __name__ == "__main__":
    main()
