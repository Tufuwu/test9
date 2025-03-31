from tests.constants import GO_EP1_ID


def test_multiple_argument_options(run_line):
    """
    Runs endpoint create with two --shared options
    Confirms exit code is 2 after click.BadParamater is raised
    """
    result = run_line(
        (
            "globus endpoint create ep_name "
            "--shared {0}:/ --shared {0}:/".format(GO_EP1_ID)
        ),
        assert_exit_code=2,
    )

    assert "Invalid value for '--shared'" in result.output
    assert "Option used multiple times." in result.output


def test_multiple_flag_options(run_line):
    """
    Runs endpoint create with two --personal options
    Confirms exit code is 2 after click.BadParamater is raised
    """
    result = run_line(
        "globus endpoint create ep_name --personal --personal", assert_exit_code=2
    )

    assert "Invalid value for '--personal'" in result.output
    assert "Option used multiple times." in result.output
