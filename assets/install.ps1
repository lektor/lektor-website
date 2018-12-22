$InstallScript = @"
import os
import sys
import json
import tempfile
import tarfile
import shutil
from subprocess import Popen
try: # py3
    from urllib.request import urlopen
    from winreg import OpenKey, CloseKey, QueryValueEx, SetValueEx, \
                   HKEY_CURRENT_USER, KEY_ALL_ACCESS, REG_EXPAND_SZ
except ImportError: # py2
    from urllib import urlopen
    from _winreg import OpenKey, CloseKey, QueryValueEx, SetValueEx, \
                   HKEY_CURRENT_USER, KEY_ALL_ACCESS, REG_EXPAND_SZ

import ctypes
from ctypes.wintypes import HWND, UINT, WPARAM, LPARAM, LPVOID


VENV_URL = 'https://pypi.python.org/pypi/virtualenv/json'
APPDATA = os.environ['LocalAppData']
APP = 'lektor-cli'
LIB = 'lib'
ROOT_KEY = HKEY_CURRENT_USER
SUB_KEY = 'Environment'
LRESULT = LPARAM
HWND_BROADCAST = 0xFFFF
WM_SETTINGCHANGE = 0x1A

PY2 = sys.version_info[0] == 2
if PY2:
    input = raw_input


def get_confirmation():
    while 1:
        user_input = input('Continue? [Yn] ').lower().strip()
        if user_input in ('', 'y'):
            break
        elif user_input == 'n':
            print()
            print('Aborted!')
            sys.exit()

def find_location():
    install_dir = os.path.join(APPDATA, APP)
    return install_dir, os.path.join(install_dir, LIB)

def deletion_error(func, path, excinfo):
    print('Problem deleting {}'.format(path))
    print('Please try and delete {} manually'.format(path))
    print('Aborted!')
    sys.exit()

def wipe_installation(install_dir):
    shutil.rmtree(install_dir, onerror=deletion_error)

def check_installation(install_dir):
    if os.path.exists(install_dir):
        print('   Lektor seems to be installed already.')
        print('   Continuing will delete:')
        print('   %s' % install_dir)
        print()
        get_confirmation()
        print()
        wipe_installation(install_dir)

def fail(message):
    print('Error: %s' % message)
    sys.exit(1)

def add_to_path(location):
    reg_key = OpenKey(ROOT_KEY, SUB_KEY, 0, KEY_ALL_ACCESS)

    try:
        path_value, _ = QueryValueEx(reg_key, 'Path')
    except WindowsError:
        path_value = ''

    paths = path_value.split(';')
    if location not in paths:
        paths.append(location)
        path_value = ';'.join(paths)
        SetValueEx(reg_key, 'Path', 0, REG_EXPAND_SZ, path_value)

    SendMessage = ctypes.windll.user32.SendMessageW
    SendMessage.argtypes = HWND, UINT, WPARAM, LPVOID
    SendMessage.restype = LRESULT
    SendMessage(HWND_BROADCAST, WM_SETTINGCHANGE, 0, u'Environment')

def _fetch_virtualenv():
    for url in json.load(urlopen(VENV_URL))['urls']:
        if url['python_version'] == 'source':
            virtualenv_url = url['url']
            #stripping '.tar.gz'
            virtualenv_filename = url['filename'][:-7]
            break
    else:
        fail('Could not find virtualenv')

    t = tempfile.mkdtemp()
    with open(os.path.join(t, 'virtualenv.tar.gz'), 'wb') as f:
        download = urlopen(virtualenv_url)
        f.write(download.read())
        download.close()
    with tarfile.open(os.path.join(t, 'virtualenv.tar.gz'), 'r:gz') as tar:
        tar.extractall(path=t)

    return os.path.join(t, virtualenv_filename)

def install_virtualenv(target_dir):
    # recent python versions include virtualenv
    cmd = [sys.executable, '-m', 'venv', target_dir]

    try:
        import venv
    except ImportError:
        venv_dir = _fetch_virtualenv()
        venv_file = os.path.join(venv_dir, 'virtualenv.py')
        # in recent versions "virtualenv.py" moved to the "src" subdirectory
        if not os.path.exists(venv_file):
            venv_file = os.path.join(venv_dir, 'src', 'virtualenv.py')

        cmd = [sys.executable, venv_file, target_dir]

    Popen(cmd).wait()

def install(install_dir, lib_dir):
    os.makedirs(install_dir)
    os.makedirs(lib_dir)

    install_virtualenv(lib_dir)

    scripts = os.path.join(lib_dir, 'Scripts')
    Popen([os.path.join(scripts, 'pip.exe'),
           'install', '--upgrade', 'Lektor'],
           cwd=scripts).wait()

    with open(os.path.join(install_dir, 'lektor.cmd'), 'w') as link_file:
        link_file.write('@echo off\n')
        link_file.write('\"' + os.path.join(scripts, 'lektor.exe') + '\"' + ' %*')

    add_to_path(install_dir)


def main():
    print()
    print('Welcome to Lektor')
    print()
    print('This script will install Lektor on your computer.')
    print()

    install_dir, lib_dir = find_location()

    check_installation(install_dir)

    print('   Installing at:')
    print('   %s' % install_dir)
    print()
    get_confirmation()

    install(install_dir, lib_dir)

    print()
    print('All done!')

main()
"@


if (Get-Command python) { python -c $InstallScript } else { "To use this script you need to have Python installed"; exit }
