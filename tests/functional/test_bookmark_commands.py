import json
import uuid

import pytest

from tests.constants import GO_EP1_ID


@pytest.fixture
def gen_bookmark_name(created_bookmark_names):
    def f(name=""):
        if name:
            name = name + "-"
        bmname = "{}{}".format(name, str(uuid.uuid1()))
        created_bookmark_names.append(bmname)
        return bmname

    return f


@pytest.fixture
def bookmark1(gen_bookmark_name, tc):
    bm1name = gen_bookmark_name(name="bm1")
    res = tc.create_bookmark(
        {"endpoint_id": GO_EP1_ID, "path": "/home/", "name": bm1name}
    )
    bm1id = res["id"]
    return (bm1name, bm1id)


@pytest.fixture
def bm1name(bookmark1):
    return bookmark1[0]


@pytest.fixture
def bm1id(bookmark1):
    return bookmark1[1]


def test_bookmark_create(gen_bookmark_name, run_line):
    """
    Runs bookmark create, confirms simple things about text and json output
    """
    result = run_line(
        ("globus bookmark create " "{}:{} {}").format(
            GO_EP1_ID, "/share/", gen_bookmark_name(name="sharebm")
        )
    )
    assert "Bookmark ID: " in result.output

    bm2name = gen_bookmark_name(name="share bookmark 2")
    json_output = json.loads(
        run_line(
            ('globus bookmark create -F json {}:{} "{}"').format(
                GO_EP1_ID, "/share/dne/", bm2name
            )
        ).output
    )
    assert json_output["name"] == bm2name
    assert json_output["path"] == "/share/dne/"
    assert json_output["endpoint_id"] == GO_EP1_ID


def test_bookmark_show(gen_bookmark_name, bm1name, bm1id, run_line):
    """
    Runs bookmark show on bm1's name and id.
    Confirms both inputs work, and verbose output is as expected.
    """
    # id
    result = run_line('globus bookmark show "{}"'.format(bm1id))
    assert "{}:/home/\n".format(GO_EP1_ID) == result.output

    # name
    result = run_line('globus bookmark show "{}"'.format(bm1name))
    assert "{}:/home/\n".format(GO_EP1_ID) == result.output

    # verbose
    result = run_line("globus bookmark show -v {}".format(bm1id))
    assert "Endpoint ID: {}".format(GO_EP1_ID) in result.output


def test_bookmark_rename_by_id(gen_bookmark_name, run_line, bm1id):
    """
    Runs bookmark rename on bm1's id. Confirms can be shown by new name.
    """
    new_name = gen_bookmark_name(name="new_bm1")
    result = run_line('globus bookmark rename "{}" "{}"'.format(bm1id, new_name))
    assert "Success" in result.output

    result = run_line('globus bookmark show -v "{}"'.format(new_name))
    assert "ID:          {}".format(bm1id) in result.output


def test_bookmark_rename_by_name(gen_bookmark_name, run_line, bm1name, bm1id):
    """
    Runs bookmark rename on bm1's name. Confirms can be shown by new name.
    """
    new_name = gen_bookmark_name(name="new_bm1")
    result = run_line('globus bookmark rename "{}" "{}"'.format(bm1name, new_name))
    assert "Success" in result.output

    result = run_line('globus bookmark show -v "{}"'.format(new_name))
    assert "ID:          {}".format(bm1id) in result.output


def test_bookmark_delete_by_id(gen_bookmark_name, run_line, bm1id):
    """
    Runs bookmark delete on bm1's id. Confirms success message.
    """
    result = run_line('globus bookmark delete "{}"'.format(bm1id))
    assert "deleted successfully" in result.output


def test_bookmark_delete_by_name(gen_bookmark_name, run_line, bm1name):
    """
    Runs bookmark delete on bm1's name. Confirms success message.
    """
    result = run_line('globus bookmark delete "{}"'.format(bm1name))
    assert "deleted successfully" in result.output
