import shlex
from logging import Logger

import os
import subprocess
from typing import List, Any, AnyStr, Optional, Tuple, Dict

from lib import models
from lib.models import TaskStatus, Action


def run_command_gracefully(command: List[str],
                           input: Optional[AnyStr] = None,
                           capture_output: bool = False,
                           timeout: float = 0,
                           check: bool = False,
                           terminate_timeout: float = 3,
                           **kwargs: Any
                           ) -> Tuple[subprocess.CompletedProcess, bool]:
    """Wrapper around Popen from subprocess, shuts the process down gracefully

        First sends SIGTERM, waits for "terminate_timeout" seconds and if
        the timeout occurs the second time, sends SIGKILL.

        It's similar to "run" function from subprocess module.

        :param command: command to run
        :param input: see corresponding "run" parameter
        :param capture_output: see corresponding "run" parameter
        :param timeout: "soft" timeout, after which the SIGTERM is sent
        :param check: see corresponding "run" parameter
        :param terminate_timeout: the "hard" timeout to wait after the SIGTERM
        :return: tuple of CompletedProcess instance and "killed" boolean
    """
    if input is not None:
        kwargs['stdin'] = subprocess.PIPE

    if capture_output:
        kwargs['stdout'] = subprocess.PIPE
        kwargs['stderr'] = subprocess.PIPE

    killed = False
    with subprocess.Popen(command, **kwargs) as proc:
        try:
            stdout, stderr = proc.communicate(input, timeout=timeout)
        except subprocess.TimeoutExpired:
            proc.terminate()
            try:
                stdout, stderr = proc.communicate(
                    input,
                    timeout=terminate_timeout,
                )
            except subprocess.TimeoutExpired:
                proc.kill()
                killed = True
                stdout, stderr = proc.communicate()
            except:  # noqa: E722
                proc.kill()
                raise

            raise subprocess.TimeoutExpired(
                proc.args,
                timeout=timeout,
                output=stdout,
                stderr=stderr,
            )
        except:  # noqa: E722
            proc.kill()
            raise

        retcode = proc.poll()

        if check and retcode:
            raise subprocess.CalledProcessError(
                retcode,
                proc.args,
                output=stdout,
                stderr=stderr
            )

    res_proc: subprocess.CompletedProcess = subprocess.CompletedProcess(
        args=proc.args, returncode=retcode,
        stdout=stdout, stderr=stderr,
    )
    return res_proc, killed


def get_patched_environ(env_path: str) -> Dict[str, str]:
    """Add path to the environment variable

        :param env_path: path to be inserted to environment
    """
    env = os.environ.copy()
    env['PATH'] = f"{env_path}:{env['PATH']}"
    return env


def run_generic_command(command: List,
                        action: Action,
                        env_path: str,
                        timeout: int,
                        team_name: str,
                        logger: Logger) -> models.CheckerVerdict:
    """Runs generic checker command, calls "run_command_gracefully"
        and handles exceptions

    :param command: command to run
    :param action: type of command (for logging)
    :param env_path: path to insert into environment
    :param timeout: "soft" command timeout
    :param team_name: team name for logging
    :param logger: logger instance
    :return: models.CheckerVerdict instance
    """
    env = get_patched_environ(env_path=env_path)

    try:
        result, killed = run_command_gracefully(
            command,
            capture_output=True,
            timeout=timeout,
            env=env,
        )

        if killed:
            logger.warning(
                f'Process was forcefully killed during {action} '
                f'for team {team_name} task '
            )

        try:
            status = TaskStatus(result.returncode)
            public_message = result.stdout[:1024].decode().strip()
            private_message = result.stderr[:1024].decode().strip()
            if status == TaskStatus.CHECK_FAILED:
                logger.warning(
                    f'{action} for team {team_name} failed with '
                    f'exit code {result.returncode},'
                    f'\nstderr: {result.stderr},\nstdout: {result.stdout}'
                )
        except ValueError as e:
            status = TaskStatus.CHECK_FAILED
            public_message = 'Check failed'
            private_message = f'Check failed with ValueError: {str(e)}'
            logger.warning(
                f'{action} for team {team_name} failed with '
                f'exit code {result.returncode},'
                f'\nstderr: {result.stderr},\nstdout: {result.stdout}'
            )

    except subprocess.TimeoutExpired:
        status = TaskStatus.DOWN
        private_message = f'{action} timeout (killed by ForcAD)'
        public_message = 'Timeout'

    command_str = ' '.join(shlex.quote(x) for x in command)
    verdict = models.CheckerVerdict(
        public_message=public_message,
        private_message=private_message,
        command=command_str,
        action=action,
        status=status
    )

    return verdict
