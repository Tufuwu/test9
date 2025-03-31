import json
import re

from tests.constants import GO_EP1_ID


def test_gcp_creation(run_line, created_endpoints):
    """
    Runs endpoint create with --personal
    Confirms personal endpoint is created successfully
    """
    result = run_line("globus endpoint create --personal personal_create -F json")
    res = json.loads(result.output)
    assert res["DATA_TYPE"] == "endpoint_create_result"
    assert res["code"] == "Created"
    assert "id" in res
    # track asset for cleanup
    created_endpoints.append(res["id"])


def test_shared_creation(run_line, created_endpoints):
    """
    Runs endpoint create with --shared and a host path
    Confirms shared endpoint is created successfully
    """
    result = run_line(
        "globus endpoint create share_create "
        "-F json --shared {}:/~/".format(GO_EP1_ID)
    )
    res = json.loads(result.output)
    assert res["DATA_TYPE"] == "endpoint_create_result"
    assert res["code"] == "Created"
    assert "Shared endpoint" in res["message"]
    assert "id" in res
    # track asset for cleanup
    created_endpoints.append(res["id"])


def test_gcs_creation(run_line, created_endpoints):
    """
    Runs endpoint create with --server
    Confirms endpoint is created successfully
    """
    result = run_line("globus endpoint create gcs_create " "--server -F json")
    res = json.loads(result.output)
    assert res["DATA_TYPE"] == "endpoint_create_result"
    assert res["code"] == "Created"
    assert res["globus_connect_setup_key"] is None
    assert "id" in res
    # track asset for cleanup
    created_endpoints.append(res["id"])


def test_text_ouptut(run_line, created_endpoints):
    """
    Creates GCP and GCS endpoint
    Confirms (non)presence of setup key in text output
    """
    # GCP
    result = run_line("globus endpoint create gcp_text --personal")
    assert "Setup Key:" in result.output
    ep_id = re.search(r"Endpoint ID:\s*(\S*)", result.output).group(1)
    created_endpoints.append(ep_id)

    # GCS
    result = run_line("globus endpoint create gcs_text --server")
    assert "Setup Key:" not in result.output
    ep_id = re.search(r"Endpoint ID:\s*(\S*)", result.output).group(1)
    created_endpoints.append(ep_id)


def test_general_options(run_line, tc, created_endpoints):
    """
    Creates a shared, personal, and server endpoints using options
    available for all endpoint types. Confirms expected values through SDK
    """
    # options with the same option value and expected value
    same_value_dict = [
        {"opt": "--description", "key": "description", "val": "sometext"},
        {"opt": "--default-directory", "key": "default_directory", "val": "/share/"},
        {"opt": "--organization", "key": "organization", "val": "someorg"},
        {"opt": "--department", "key": "department", "val": "somedept"},
        {"opt": "--keywords", "key": "keywords", "val": "some,key,words"},
        {"opt": "--contact-email", "key": "contact_email", "val": "a@b.c"},
        {"opt": "--contact-info", "key": "contact_info", "val": "info"},
        {"opt": "--info-link", "key": "info_link", "val": "http://a.b"},
    ]
    # options that have differing option values and expected values
    diff_value_dict = [
        {
            "opt": "--force-encryption",
            "key": "force_encryption",
            "val": "",
            "expected": True,
        },
        {
            "opt": "--disable-verify",
            "key": "disable_verify",
            "val": "",
            "expected": True,
        },
    ]

    # for each endpoint type
    for ep_type in ["--shared {}:/~/".format(GO_EP1_ID), "--personal", "--server"]:

        # make and run the line, get and track the id for cleanup
        line = "globus endpoint create general_options " "-F json {} ".format(ep_type)
        for item in same_value_dict + diff_value_dict:
            line += "{} {} ".format(item["opt"], item["val"])
        ep_id = json.loads(run_line(line).output)["id"]
        created_endpoints.append(ep_id)

        # get and confirm values from SDK get_endpoint
        res = tc.get_endpoint(ep_id)
        for item in same_value_dict:
            assert item["val"] == res[item["key"]]
        for item in diff_value_dict:
            assert item["expected"] == res[item["key"]]


def test_server_only_options(run_line, tc, created_endpoints):
    """
    Runs endpoint create with options only valid for GCS
    Confirms expected values gotten through SDK
    """
    # options with the same option value and expected value
    same_value_dict = [
        {"opt": "--myproxy-dn", "key": "myproxy_dn", "val": "/dn"},
        {"opt": "--myproxy-server", "key": "myproxy_server", "val": "srv.example.com"},
    ]
    # options that have differing option values and expected values
    diff_value_dict = [
        {"opt": "--private", "key": "public", "val": "", "expected": False},
        {
            "opt": "--location",
            "key": "location",
            "val": "1.1,2",
            "expected": "1.10,2.00",
        },
    ]

    # make and run the line, get and track the id for cleanup
    line = "globus endpoint create valid_gcs " "--server -F json "
    for item in same_value_dict + diff_value_dict:
        line += "{} {} ".format(item["opt"], item["val"])
    ep_id = json.loads(run_line(line).output)["id"]
    created_endpoints.append(ep_id)

    # get and confirm values from SDK get_endpoint
    res = tc.get_endpoint(ep_id)
    for item in same_value_dict:
        assert item["val"] == res[item["key"]]
    for item in diff_value_dict:
        assert item["expected"] == res[item["key"]]


# TODO: test against a managed endpoint
# def test_valid_managed_options(run_line):


def test_invalid_gcs_only_options(run_line):
    """
    For all GCS only options, tries to create a GCP and shared endpoint
    Confirms invalid options are caught at the CLI level rather than API
    """
    options = [
        "--public",
        "--private",
        "--myproxy-dn /dn",
        "--myproxy-server mpsrv.example.com",
        "--oauth-server oasrv.example.com",
        "--location 1,1",
    ]
    for opt in options:
        for ep_type in ["--shared {}:/~/".format(GO_EP1_ID), "--personal"]:
            result = run_line(
                ("globus endpoint create invalid_gcs " "{} {} ".format(ep_type, opt)),
                assert_exit_code=2,
            )
            assert "Globus Connect Server" in result.output


def test_invalid_managed_only_options(run_line):
    """
    For all managed only options, tries to create a GCS endpoint
    Confirms invalid options are caught at the CLI level rather than AP
    """
    options = [
        "--network-use custom",
        "--max-concurrency 2",
        "--preferred-concurrency 1",
        "--max-parallelism 2",
        "--preferred-parallelism 1",
    ]
    for opt in options:
        result = run_line(
            ("globus endpoint create invalid_managed " "--server {}".format(opt)),
            assert_exit_code=2,
        )
        assert "managed endpoints" in result.output
