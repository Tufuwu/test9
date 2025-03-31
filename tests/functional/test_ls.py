from tests.constants import GO_EP1_ID


def test_path(run_line):
    """
    Does an ls on EP1:/, confirms expected results.
    """
    path = "/"
    result = run_line("globus ls {}:{}".format(GO_EP1_ID, path))

    expected = ["home/", "mnt/", "not shareable/", "share/"]
    for item in expected:
        assert item in result.output


def test_recursive(run_line):
    """
    Confirms --recursive ls on EP1:/share/ finds file1.txt
    """
    result = run_line("globus ls -r {}:/share/".format(GO_EP1_ID))
    assert "file1.txt" in result.output


def test_depth(run_line):
    """
    Confirms setting depth to 1 on a --recursive ls of EP1:/
    finds godata but not file1.txt
    """
    result = run_line(("globus ls -r --recursive-depth-limit 1 {}:/".format(GO_EP1_ID)))
    assert "file1.txt" not in result.output


def test_recursive_json(run_line):
    """
    Confirms -F json works with the RecursiveLsResponse
    """
    result = run_line("globus ls -r -F json {}:/share".format(GO_EP1_ID))
    assert '"DATA":' in result.output
    assert '"name": "godata/file1.txt"' in result.output
