import json
import logging
import os
import shlex
from datetime import datetime, timedelta

import globus_sdk
import pytest
import six
from click.testing import CliRunner

from globus_cli.services.auth import get_auth_client
from globus_cli.services.transfer import get_client as get_transfer_client
from tests.constants import GO_EP1_ID
from tests.utils import patch_config

log = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def test_file_dir():
    return os.path.normpath(os.path.join(os.path.dirname(__file__), "files"))


@pytest.fixture
def user_data(test_file_dir):
    ret = {}
    for uname in ("clitester1a", "clitester1alinked", "go"):
        with open(os.path.join(test_file_dir, uname + "@globusid.org.json")) as f:
            ret[uname] = json.load(f)
    return ret


@pytest.fixture(scope="session", autouse=True)
def clean_sharing():
    """
    Cleans out any files in ~/.globus/sharing/ on go#ep1 older than an hour at the start
    of each testsuite run
    """
    with patch_config():
        tc = get_transfer_client()

        path = "~/.globus/sharing/"
        hour_ago = datetime.utcnow() - timedelta(hours=1)
        filter_string = "last_modified:," + hour_ago.strftime("%Y-%m-%d %H:%M:%S")
        try:
            old_files = tc.operation_ls(
                GO_EP1_ID, path=path, filter=filter_string, num_results=None
            )
        except globus_sdk.TransferAPIError:
            return

        kwargs = {"notify_on_succeeded": False, "notify_on_fail": False}
        ddata = globus_sdk.DeleteData(tc, GO_EP1_ID, **kwargs)

        for item in old_files:
            ddata.add_item(path + item["name"])

        if len(ddata["DATA"]):
            tc.submit_delete(ddata)


@pytest.fixture
def cli_runner():
    return CliRunner()


@pytest.fixture
def run_line(cli_runner, request):
    """
    Uses the CliRunner to run the given command line.

    Any calls to get_config_obj during the test are patched to
    return a ConfigObj with given config dict. If no config dict is given,
    defaults to default_test_config_obj defined above.

    Asserts that the exit_code is equal to the given assert_exit_code,
    and if that exit_code is 0 prevents click from catching exceptions
    for easier debugging.
    """

    def func(line, config=None, assert_exit_code=0, stdin=None):
        from globus_cli import main

        with patch_config(config):
            # split line into args and confirm line starts with "globus"
            # python2 shlex can't handle non ascii unicode
            if six.PY2 and isinstance(line, six.text_type):
                args = [a for a in shlex.split(line.encode("utf-8"))]
            else:
                args = shlex.split(line)
            assert args[0] == "globus"

            # run the line. globus_cli.main is the "globus" part of the line
            # if we are expecting success (0), don't catch any exceptions.
            result = cli_runner.invoke(
                main, args[1:], input=stdin, catch_exceptions=bool(assert_exit_code)
            )
            assert result.exit_code == assert_exit_code
            return result

    return func


@pytest.fixture
def tc():
    with patch_config():
        return get_transfer_client()


@pytest.fixture
def ac():
    with patch_config():
        return get_auth_client()


# magical cleanup collections
# each of these fixtures records data to pass through the autocleaner
@pytest.fixture
def created_endpoints():
    return []


@pytest.fixture
def created_bookmark_names():
    return []


@pytest.fixture(autouse=True)
def autoclean(request, created_endpoints, created_bookmark_names, tc):
    def clean_endpoints():
        for x in created_endpoints:
            tc.delete_endpoint(x)

    def clean_bookmarks():
        if not created_bookmark_names:
            return

        for bm in tc.bookmark_list():
            if bm["name"] in created_bookmark_names:
                try:
                    tc.delete_bookmark(bm["id"])
                except globus_sdk.GlobusAPIError:
                    log.exception("API error on bookmark tests cleanup")
                except globus_sdk.NetworkError:
                    log.exception("Network error on bookmark tests cleanup")

    def clean():
        clean_endpoints()
        clean_bookmarks()

    request.addfinalizer(clean)
