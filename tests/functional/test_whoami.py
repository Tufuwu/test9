def test_verbose(run_line, user_data):
    """
    Confirms --verbose includes Name, Email, and ID fields.
    """
    result = run_line("globus whoami --verbose")
    for field in ["Username", "Name", "Email", "ID"]:
        assert field in result.output
    for field in ["username", "name", "email", "id"]:
        assert user_data["clitester1a"][field] in result.output


def test_linked_identities(run_line, user_data):
    """
    Confirms --linked-identities sees cliester1a-linked#globusid.org
    """
    result = run_line("globus whoami --linked-identities")
    assert user_data["clitester1a"]["username"] in result.output
    assert user_data["clitester1alinked"]["username"] in result.output


def test_verbose_linked_identities(run_line, user_data):
    """
    Confirms combining --verbose and --linked-identities has expected
    values present for the whole identity set.
    """
    result = run_line("globus whoami --linked-identities -v")
    for field in ["Username", "Name", "Email", "ID"]:
        assert field in result.output
    for field in ["username", "name", "email", "id"]:
        assert user_data["clitester1a"][field] in result.output
        assert user_data["clitester1alinked"][field] in result.output
