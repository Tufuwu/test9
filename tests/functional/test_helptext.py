"""
tests which ensure that helptext rendering is correct
"""


# This is a regression test for
#   https://github.com/globus/globus-cli/issues/496
def test_helptext_for_commands_with_security_principal_opts(run_line):
    """
    Test commands which use the security principal options and ensure that their
    helptext renders correctly.
    """
    result = run_line("globus endpoint role create --help")
    assert "Create a role on an endpoint" in result.output

    result = run_line("globus endpoint permission create --help")
    assert "Create a new access control rule on the target endpoint" in result.output
