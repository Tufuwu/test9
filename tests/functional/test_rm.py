import json
from random import getrandbits

from tests.constants import GO_EP1_ID


def _load_probably_json_substring(x):
    """
    Weak method of extracting JSON object from a string which includes JSON and
    non-JSON data. Just gets the largest substring from { to }
    Works well for these cases, where click.CliRunner gives us output
    containing both stderr and stdout.
    """
    return json.loads(x[x.index("{") : x.rindex("}") + 1])


def test_recursive(run_line, tc):
    """
    Makes a dir on ep1, then --recursive rm's it.
    Confirms delete task was successful.
    """
    # name randomized to prevent collision
    path = "/~/rm_dir-{}".format(str(getrandbits(128)))
    tc.operation_mkdir(GO_EP1_ID, path)

    result = run_line("globus rm -r -F json {}:{}".format(GO_EP1_ID, path))
    res = _load_probably_json_substring(result.output)
    assert res["status"] == "SUCCEEDED"


def test_no_file(run_line):
    """
    Attempts to remove a non-existant file. Confirms exit code 1
    """
    path = "/~/nofilehere.txt"
    run_line("globus rm {}:{}".format(GO_EP1_ID, path), assert_exit_code=1)


def test_ignore_missing(run_line):
    """
    Attempts to remove a non-existant file path, with --ignore-missing.
    Confirms exit code 0 and silent output.
    """
    path = "/~/nofilehere.txt"
    result = run_line("globus rm -f {}:{}".format(GO_EP1_ID, path))
    assert "Delete task submitted under ID " in result.output


def test_pattern_globbing(run_line, tc):
    """
    Makes 3 dirs with the same prefix, and uses * globbing to rm them all.
    Confirms delete task was successful and removed 3 dirs.
    """
    # mark all dirs with a random generated prefix to prevent collision
    rand = str(getrandbits(128))
    for i in range(3):
        path = "/~/rm_dir{}-{}".format(rand, i)
        tc.operation_mkdir(GO_EP1_ID, path)

    # remove all dirs with the prefix
    glob = "rm_dir{}*".format(rand)
    result = run_line("globus rm -r -F json {}:{}".format(GO_EP1_ID, glob))
    res = _load_probably_json_substring(result.output)
    assert res["status"] == "SUCCEEDED"

    # confirm no dirs with the prefix exist on the endpoint
    filter_string = "name:~rm_dir{}*".format(rand)
    ls_doc = tc.operation_ls(GO_EP1_ID, filter=filter_string)
    assert list(ls_doc) == []


def test_wild_globbing(run_line, tc):
    """
    Makes 3 dirs with the same prefix, and uses ? globbing to rm them all.
    Confirms delete task was successful and removed 3 dirs.
    """
    # mark all dirs with a random generated prefix to prevent collision
    rand = str(getrandbits(128))
    for i in range(3):
        path = "/~/rm_dir{}-{}".format(rand, i)
        tc.operation_mkdir(GO_EP1_ID, path)

    # remove all dirs with the prefix
    glob = "rm_dir{}-?".format(rand)
    result = run_line("globus rm -r -F json {}:{}".format(GO_EP1_ID, glob))
    res = _load_probably_json_substring(result.output)
    assert res["status"] == "SUCCEEDED"

    # confirm no dirs with the prefix exist on the endpoint
    filter_string = "name:~rm_dir{}*".format(rand)
    ls_doc = tc.operation_ls(GO_EP1_ID, filter=filter_string)
    assert list(ls_doc) == []


def test_bracket_globbing(run_line, tc):
    """
    Makes 3 dirs with the same prefix, and uses [] globbing to rm them all.
    Confirms delete task was successful and removed 3 dirs.
    """
    # mark all dirs with a random generated prefix to prevent collision
    rand = str(getrandbits(128))
    for i in range(3):
        path = "/~/rm_dir{}-{}".format(rand, i)
        tc.operation_mkdir(GO_EP1_ID, path)

    # remove all dirs with the prefix
    glob = "rm_dir{}-[012]".format(rand)
    result = run_line("globus rm -r -F json {}:{}".format(GO_EP1_ID, glob))
    res = _load_probably_json_substring(result.output)
    assert res["status"] == "SUCCEEDED"

    # confirm no dirs with the prefix exist on the endpoint
    filter_string = "name:~rm_dir{}*".format(rand)
    ls_doc = tc.operation_ls(GO_EP1_ID, filter=filter_string)
    assert list(ls_doc) == []


def test_timeout(run_line):
    """
    Attempts to remove a path we are not allowed to remove,
    confirms rm times out and exits 1 after given timeout.
    """
    timeout = 2
    path = "/share/godata/file1.txt"
    result = run_line(
        "globus rm -r --timeout {} {}:{}".format(timeout, GO_EP1_ID, path),
        assert_exit_code=1,
    )
    assert (
        "Task has yet to complete " "after {} seconds".format(timeout)
    ) in result.output


def test_timeout_explicit_status(run_line):
    """
    Attempts to remove a path we are not allowed to remove,
    confirms rm times out and exits STATUS after given timeout, where
    STATUS is set via the --timeout-exit-code opt
    """
    timeout = 1
    status = 50
    path = "/share/godata/file1.txt"
    result = run_line(
        "globus rm -r --timeout {} --timeout-exit-code {} {}:{}".format(
            timeout, status, GO_EP1_ID, path
        ),
        assert_exit_code=status,
    )
    assert (
        "Task has yet to complete " "after {} seconds".format(timeout)
    ) in result.output
