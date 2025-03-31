import pytest
from click.testing import CliRunner


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def run_command(runner):
    def _run(cmd, args, exit_code=0):
        result = runner.invoke(cmd, args, catch_exceptions=bool(exit_code))
        assert result.exit_code == exit_code
        return result

    return _run
