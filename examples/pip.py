from pyinfra import host
from pyinfra.operations import apk, apt, files, pip, python, yum

SUDO = True

if host.fact.linux_name in ['Alpine']:
    apk.packages(
        name='Install packages for python virtual environments',
        packages=[
            'gcc',
            'libffi-dev',
            'make',
            'musl-dev',
            'openssl-dev',
            'py3-pynacl',
            'py3-virtualenv',
            'python3-dev',
        ],
    )

if host.fact.linux_name in ['CentOS']:
    yum.packages(
        name='Install pip3 so you can install virtualenv',
        packages='python3-pip',
    )

if host.fact.linux_name in ['Ubuntu']:
    apt.packages(
        name='Install pip3 so you can install virtualenv',
        packages='python3-pip',
        update=True,
    )

if not host.fact.file('/usr/bin/pip'):
    files.link(
        name='Create link /usr/bin/pip that points to /usr/bin/pip3',
        path='/usr/bin/pip',
        target='/usr/bin/pip3',
    )

pip.packages(
    name='Install virtualenv using pip',
    packages='virtualenv',
)

pip.virtualenv(
    name='Create a virtualenv',
    path='/usr/local/bin/venv',
)

# use that virtualenv to install pyinfra
pip.packages(
    name='Install pyinfra into a virtualenv',
    packages='pyinfra',
    virtualenv='/usr/local/bin/venv',
)


# Show that we can actually run the pyinfra command from that virtualenv
def run_pyinfra_version(state, host):
    status, stdout, stderr = host.run_shell_command(
        '/usr/local/bin/venv/bin/pyinfra --version',
        env={'LC_ALL': 'C.UTF-8', 'LANG': 'C.UTF-8,'},
    )
    assert status, 'pyinfra command failed: {0}'.format((stdout, stderr))
    assert 'pyinfra: ' in stdout[0]

python.call(run_pyinfra_version)  # noqa: E305
