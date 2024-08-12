import pytest

from ssonar.runner import BaseRunner


class DummyRunner(BaseRunner):
    def job(self) -> None:
        pass


@pytest.fixture
def runner():
    dummy = DummyRunner(1)
    return dummy


@pytest.mark.parametrize("delay_sec", [0, 0.1, 23])
def test_delay_sc_valid_values(delay_sec):
    runner = DummyRunner(delay_sec)
    assert runner.delay_sec == delay_sec


@pytest.mark.parametrize("delay_sec", [-0.1, -1, -100])
def test_delay_sc_invalid_values(delay_sec):
    with pytest.raises(ValueError):
        DummyRunner(delay_sec)


def test_default_run_property_value(runner):
    assert runner.is_running is False


def test_stop_method(runner):
    runner.stop()
    assert runner.is_running is False
