import sys
import subprocess


def _install_required_package(cr):
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'authlib'])
