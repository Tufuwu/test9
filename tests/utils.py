import os
from contextlib import contextmanager

from configobj import ConfigObj

import globus_cli.config
from tests.constants import (
    CLITESTER1A_AUTH_RT,
    CLITESTER1A_CLIENT_ID,
    CLITESTER1A_CLIENT_SECRET,
    CLITESTER1A_TRANSFER_RT,
)

try:
    import mock
except ImportError:
    from unittest import mock


def on_windows():
    return os.name == "nt"


def get_default_test_config():
    """
    Returns a ConfigObj with the clitester's refresh tokens as if the
    clitester was logged in and a call to get_config_obj was made.
    """
    # create a ConfgObj from a dict of testing constants. a ConfigObj created
    # this way will not be tied to a config file on disk, meaning that
    # ConfigObj.filename = None and ConfigObj.write() returns a string without
    # writing anything to disk.
    return ConfigObj(
        {
            "cli": {
                globus_cli.config.CLIENT_ID_OPTNAME: CLITESTER1A_CLIENT_ID,
                globus_cli.config.CLIENT_SECRET_OPTNAME: CLITESTER1A_CLIENT_SECRET,
                globus_cli.config.AUTH_RT_OPTNAME: CLITESTER1A_AUTH_RT,
                globus_cli.config.AUTH_AT_OPTNAME: "",
                globus_cli.config.AUTH_AT_EXPIRES_OPTNAME: 0,
                globus_cli.config.TRANSFER_RT_OPTNAME: CLITESTER1A_TRANSFER_RT,
                globus_cli.config.TRANSFER_AT_OPTNAME: "",
                globus_cli.config.TRANSFER_AT_EXPIRES_OPTNAME: 0,
            }
        }
    )


@contextmanager
def patch_config(conf=None):
    if conf is None:
        conf = get_default_test_config()

    with mock.patch("globus_cli.config.get_config_obj", return_value=conf):
        yield
