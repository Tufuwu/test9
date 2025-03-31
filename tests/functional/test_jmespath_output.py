import json

from tests.constants import GO_EP1_ID, GO_EP2_ID


def test_jmespath_noop(run_line):
    """
    Runs some simple fetch operations and confirms that `--jmespath '@'`
    doesn't change the output (but also that it overrides --format TEXT)
    """
    result = run_line("globus endpoint show {} -Fjson".format(GO_EP1_ID))
    jmespathresult = run_line(
        "globus endpoint show {} -Ftext --jmespath '@'".format(GO_EP1_ID)
    )

    # Drop fields that can be affected by concurrent test runs
    output_json_dict = json.loads(result.output)
    output_jmespath_dict = json.loads(jmespathresult.output)
    for obj in (output_json_dict, output_jmespath_dict):
        obj.pop("in_use")
        obj.pop("expire_time")
    output_fixed = json.dumps(output_json_dict)
    jmespathoutput_fixed = json.dumps(output_jmespath_dict)

    assert output_fixed == jmespathoutput_fixed


def test_jmespath_extract_from_list(run_line):
    """
    Uses jmespath to extract a value from a list result using a filter.
    Confirms that the result is identical to a direct fetch of that
    resource.
    """
    # list tutorial endpoints with a search, but extract go#ep2
    result = run_line(
        (
            "globus endpoint search 'Tutorial' "
            "--filter-owner-id go@globusid.org "
            "--jmespath 'DATA[?id==`{}`] | [0]'"
        ).format(GO_EP2_ID)
    )
    outputdict = json.loads(result.output)

    show_result = run_line("globus endpoint show {} -Fjson".format(GO_EP2_ID))
    showdict = json.loads(show_result.output)

    # check specific keys because search includes `_rank` and doesn't
    # include the server list
    # just a random selection of "probably stable" values for this test
    for k in ("id", "display_name", "owner_id", "subscription_id"):
        assert outputdict[k] == showdict[k]


def test_jmespath_no_expression_error(run_line):
    """
    Intentionally misuse `--jmespath` with no provided expression. Confirm
    that it gives a usage error.
    """
    result = run_line(
        "globus endpoint search 'Tutorial' --jmespath", assert_exit_code=2
    )
    assert "Error: --jmespath option requires an argument" in result.output

    # and the error says `--jq` if you use the `--jq` form
    result = run_line("globus endpoint search 'Tutorial' --jq", assert_exit_code=2)
    assert "Error: --jq option requires an argument" in result.output


def test_jmespath_invalid_expression_error(run_line):
    """
    Intentionally misuse `--jmespath` with a malformed expression. Confirm
    that it gives a JMESPath ParseError.
    """
    result = run_line(
        ("globus endpoint search 'Tutorial' --jmespath '{}'"), assert_exit_code=1
    )
    assert "ParseError:" in result.output
