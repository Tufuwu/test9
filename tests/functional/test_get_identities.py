import json


def test_default_one_id(run_line, user_data):
    """
    Runs get-identities with one id, confirms correct username returned
    """
    result = run_line("globus get-identities " + user_data["clitester1a"]["id"])
    assert user_data["clitester1a"]["username"] + "\n" == result.output


def test_defualt_one_username(run_line, user_data):
    """
    Runs get-identities with one username, confirms correct id returned
    """
    result = run_line("globus get-identities " + user_data["clitester1a"]["username"])
    assert user_data["clitester1a"]["id"] + "\n" == result.output


def test_default_invalid(run_line, user_data):
    """
    Runs get-identities with one username, confirms correct id returned
    """
    result = run_line("globus get-identities invalid")
    assert "NO_SUCH_IDENTITY\n" == result.output


def test_default_multiple_inputs(run_line, user_data):
    """
    Runs get-identities with id username, duplicate and invalid inputs
    Confirms order is preserved and all values are as expected
    """
    in_vals = [
        user_data["clitester1a"]["username"],
        user_data["clitester1a"]["id"],
        "invalid",
        user_data["go"]["username"],
        user_data["go"]["username"],
    ]

    expected = [
        user_data["clitester1a"]["id"],
        user_data["clitester1a"]["username"],
        "NO_SUCH_IDENTITY",
        user_data["go"]["id"],
        user_data["go"]["id"],
    ]

    result = run_line("globus get-identities " + " ".join(in_vals))
    assert "\n".join(expected) + "\n" == result.output


def test_verbose(run_line, user_data):
    """
    Runs get-identities with --verbose, confirms expected fields found
    """
    go_data = user_data["go"]
    result = run_line("globus get-identities --verbose " + go_data["id"])
    for key in ["username", "id", "name", "organization", "email"]:
        assert go_data[key] in result.output


def test_json(run_line, user_data):
    """
    Runs get-identities with -F json confirms expected values
    """
    go_data = user_data["go"]
    output = json.loads(
        run_line("globus get-identities -F json " + go_data["id"]).output
    )
    for key in go_data:
        assert go_data[key] in output["identities"][0][key]
