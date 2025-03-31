try:
    import mock
except ImportError:
    from unittest import mock


import globus_sdk

from globus_cli.config import AUTH_RT_OPTNAME, TRANSFER_RT_OPTNAME
from tests.utils import get_default_test_config


def test_login_validates_token(run_line):
    with mock.patch("globus_cli.commands.login.internal_auth_client") as m:
        ac = mock.MagicMock(spec=globus_sdk.NativeAppAuthClient)
        m.return_value = ac

        run_line("globus login")

        conf = get_default_test_config()
        a_rt = conf["cli"][AUTH_RT_OPTNAME]
        t_rt = conf["cli"][TRANSFER_RT_OPTNAME]
        ac.oauth2_validate_token.assert_any_call(a_rt)
        ac.oauth2_validate_token.assert_any_call(t_rt)
