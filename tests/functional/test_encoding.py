# -*- coding: utf8 -*-
import json
from random import getrandbits

import pytest
import six

from tests.constants import GO_EP1_ID
from tests.utils import on_windows


@pytest.fixture
def dir_operations(run_line):
    """
    Given an input directory name, makes the directory to test inputs,
    ls's the directory to test outputs and output formats,
    attempts to remake the directory to test error outputs,
    and finally deletes the directory for cleanup.
    """

    def f(input_name, expected_name=None):
        # mkdir
        # name randomized to prevent collision
        rand = str(getrandbits(128))
        dir_name = input_name + rand
        expected = (expected_name or input_name) + rand
        # if given a unicode name, run a unicode string
        if isinstance(input_name, six.text_type):
            make_output = run_line(
                u"globus mkdir {}:~/{}".format(GO_EP1_ID, dir_name)
            ).output
        # if given a byte string name, run a byte string
        else:
            make_output = run_line(
                b"globus mkdir {}:~/{}".format(GO_EP1_ID, dir_name)
            ).output

        assert "The directory was created successfully" in make_output

        # confirm the dir can be seen. Confirms simple, long, verbose,
        # and json output all handle the encoding.
        ls_output = run_line(u"globus ls {}:~/".format(GO_EP1_ID)).output
        assert expected in ls_output

        long_output = run_line(u"globus ls -l {}:~/".format(GO_EP1_ID)).output
        assert expected in long_output
        assert "Filename" in long_output

        json_output = json.loads(
            run_line(u"globus ls -F json {}:~/".format(GO_EP1_ID)).output
        )
        assert expected in [i["name"] for i in json_output["DATA"]]

        # attempt to make the dir again to test error output:
        # if given a unicode name, run a unicode string
        if isinstance(input_name, six.text_type):
            make2_output = run_line(
                u"globus mkdir {}:~/{}".format(GO_EP1_ID, dir_name), assert_exit_code=1
            ).output
        # if given a byte string name, run a byte string
        else:
            make2_output = run_line(
                b"globus mkdir {}:~/{}".format(GO_EP1_ID, dir_name), assert_exit_code=1
            ).output
        assert "Path already exists" in make2_output
        assert expected in make2_output

        # delete for cleanup:
        # if given a unicode name, run a unicode string
        if isinstance(input_name, six.text_type):
            delete_output = run_line(
                u"globus delete -r {}:~/{}".format(GO_EP1_ID, dir_name)
            ).output
        # if given a byte string name, run a byte string
        else:
            delete_output = run_line(
                b"globus delete -r {}:~/{}".format(GO_EP1_ID, dir_name)
            ).output

        assert "The delete has been accepted" in delete_output

    return f


@pytest.fixture
def ep_operations(run_line):
    """
    Given an input_name, creates, updates, gets, and deletes an endpoint
    using the input_name as a display_name. If an expected_name is given,
    confirms output matches that name rather than the input_name.
    """

    def f(input_name, expected_name=None):
        # if given a unicode name, run a unicode string
        if isinstance(input_name, six.text_type):
            create_output = json.loads(
                run_line(
                    u"globus endpoint create -F json --server {}".format(input_name)
                ).output
            )
        # if given a byte string name, run a byte string
        else:
            create_output = json.loads(
                run_line(
                    b"globus endpoint create -F json --server {}".format(input_name)
                ).output
            )
        assert create_output["code"] == "Created"
        assert create_output["code"] == "Created"
        ep_id = create_output["id"]

        # confirm endpoint show sees ep
        show_output = run_line("globus endpoint show {}".format(ep_id)).output
        assert (expected_name or input_name) in show_output

        # update
        # if given a unicode name, run a unicode string
        if isinstance(input_name, six.text_type):
            update_output = run_line(
                u"globus endpoint update {} --description {}".format(ep_id, input_name)
            ).output
        # if given a byte string name, run a byte string
        else:
            update_output = run_line(
                b"globus endpoint update {} --description {}".format(ep_id, input_name)
            ).output
        assert "updated successfully" in update_output

        # confirm show sees updated description
        show_output = json.loads(
            run_line("globus endpoint show {} -F json".format(ep_id)).output
        )
        assert (expected_name or input_name) == show_output["description"]

        # delete
        delete_output = run_line("globus endpoint delete {}".format(ep_id)).output
        assert "deleted successfully" in delete_output

    return f


def test_quote_escaping(dir_operations, ep_operations):
    """
    Tests operations with an escaped quote inside quotes that should be
    seen as one literal quote character by the shell
    """
    name = r'"\""'
    dir_operations(name, expected_name='"')
    ep_operations(name, expected_name='"')


def test_ascii_url_encoding(dir_operations, ep_operations):
    """
    Tests operations with an ASCII name that includes ' ' and '%"
    characters that will need to be encoded for use in a url.
    """
    name = '"a% b"'
    dir_operations(name, expected_name="a% b")
    ep_operations(name, expected_name="a% b")


@pytest.mark.skipif(
    six.PY2 and on_windows(), reason="python2 Windows console issues (FIXME?)"
)
def test_non_ascii_utf8(dir_operations, ep_operations):
    """
    Tests operations with a UTF-8 name containing non ASCII characters with
    code points requiring multiple bytes.
    """
    name = u"テスト"
    dir_operations(name)
    ep_operations(name)


@pytest.mark.skipif(six.PY3, reason="test run with Python 3")
@pytest.mark.skipif(
    six.PY2 and on_windows(), reason="python2 Windows console issues (FIXME?)"
)
def test_non_ascii_utf8_bytes(dir_operations, ep_operations):
    """
    Tests operations with a byte string encoded from non ASCII UTF-8.
    This test is only run on Python 2 as bytes are not strings in Python 3.
    """
    uni_name = u"テスト"
    byte_name = uni_name.encode("utf8")
    # we expect uni_name back since the API returns unicode strings
    dir_operations(byte_name, expected_name=uni_name)
    ep_operations(byte_name, expected_name=uni_name)


@pytest.mark.skipif(
    six.PY2 and on_windows(), reason="python2 Windows console issues (FIXME?)"
)
def test_latin1(dir_operations, ep_operations):
    """
    Tests operations with latin-1 name that is not valid UTF-8.
    """
    # the encoding for 'é' in latin-1 is a continuation byte in utf-8
    byte_name = b"\xe9"  # é's latin-1 encoding
    name = byte_name.decode("latin-1")
    with pytest.raises(UnicodeDecodeError):
        byte_name.decode("utf-8")

    dir_operations(name)
    ep_operations(name)


@pytest.mark.skipif(six.PY3, reason="test run with Python 3")
@pytest.mark.skipif(
    six.PY2 and on_windows(), reason="python2 Windows console issues (FIXME?)"
)
def test_invalid_utf8_bytes(run_line):
    r"""
    Tests operations with byte string that can be decoded with
    latin-1 but not with UTF-8. Confirms that this raises a
    UnicodeDecodeError, as the SDK/APIs can't handle decoding non UTF-8.
    This test is only run on Python 2 as bytes are not strings in Python 3.

    You can imitate this in the command-line using a `printf` subshell, e.g.
      globus mkdir "${GO_EP_1}:~/$(printf "\xe9")"
    """
    # the encoding for 'é' in latin-1 is a continuation byte in utf-8
    byte_name = b"\xe9"  # é's latin-1 encoding

    make_output = run_line(
        "globus mkdir {}:~/{}".format(GO_EP1_ID, byte_name), assert_exit_code=1
    ).output
    assert "UnicodeDecodeError" in make_output
