import json

import pytest


@pytest.fixture
def mk_gcs(run_line, created_endpoints):
    def f():
        result = run_line(
            "globus endpoint create endpointservertest_gcs --server -F json"
        )
        res = json.loads(result.output)
        created_endpoints.append(res["id"])
        return res["id"]

    return f


@pytest.fixture
def mk_gcp(run_line, created_endpoints):
    def f():
        result = run_line(
            "globus endpoint create endpointservertest_gcp --personal -F json"
        )
        res = json.loads(result.output)
        created_endpoints.append(res["id"])
        return res["id"]

    return f


@pytest.fixture
def add_server(run_line):
    def f(epid, hostname="foo.com", use_json=False, port=None, return_id=False):
        extra_opts = ""
        if use_json or return_id:
            extra_opts += " -Fjson"
        if port:
            extra_opts += " --port {}".format(port)

        result = run_line(
            "globus endpoint server add {} --hostname {}{}".format(
                epid, hostname, extra_opts
            )
        )

        if not return_id:
            return result.output
        else:
            return json.loads(result.output)["id"]

    return f


@pytest.fixture
def create_and_delete_server(add_server, run_line):
    def f(gcs_id, mode):
        assert mode in ("id", "hostname", "hostname_port", "uri")

        add_server_out = json.loads(add_server(gcs_id, use_json=True))

        if mode == "id":
            server = add_server_out["id"]
        elif mode == "hostname":
            server = "foo.com"
        elif mode == "hostname_port":
            server = "foo.com:2811"
        elif mode == "uri":
            server = "gsiftp://foo.com:2811"
        else:
            raise NotImplementedError

        result = run_line("globus endpoint server delete {} {}".format(gcs_id, server))
        assert "Server deleted successfully" in result.output
        result = run_line("globus endpoint server list {}".format(gcs_id))
        assert "gsiftp://foo.com:2811" not in result.output

    return f


def test_gcs_server_add(mk_gcs, add_server):
    gcs_id = mk_gcs()
    output = add_server(gcs_id)
    assert "Server added to endpoint successfully" in output


def test_gcs_server_list(run_line, mk_gcs, add_server):
    gcs_id = mk_gcs()
    add_server(gcs_id)
    result = run_line("globus endpoint server list {}".format(gcs_id))
    assert "gsiftp://foo.com:2811" in result.output


def test_gcp_server_list(run_line, mk_gcp, add_server):
    gcp_id = mk_gcp()
    result = run_line("globus endpoint server list {}".format(gcp_id))
    assert "none (Globus Connect Personal)" in result.output


@pytest.mark.parametrize("mode", ["id", "hostname", "hostname_port", "uri"])
def test_server_delete_various(mode, mk_gcs, create_and_delete_server):
    gcs_id = mk_gcs()
    create_and_delete_server(gcs_id, mode)


def test_server_delete_by_hostname_many_matches(run_line, mk_gcs, add_server):
    gcs_id = mk_gcs()
    matches = [
        add_server(gcs_id, return_id=True),
        add_server(gcs_id, port="2812", return_id=True),
        add_server(gcs_id, port="2813", return_id=True),
    ]
    nonmatch = add_server(gcs_id, hostname="foo.net", return_id=True)

    result = run_line(
        "globus endpoint server delete {} foo.com".format(gcs_id), assert_exit_code=2
    )
    assert "Multiple servers matched" in result.output
    assert str(nonmatch) not in result.output
    for m in matches:
        assert str(m) in result.output


def test_server_delete_on_gcp(run_line, mk_gcp):
    gcp_id = mk_gcp()
    result = run_line(
        "globus endpoint server delete {} foo.com".format(gcp_id), assert_exit_code=2
    )
    assert (
        "You cannot delete servers from Globus Connect Personal endpoints"
        in result.output
    )
