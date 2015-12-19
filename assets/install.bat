@echo off & python --version 2> NUL & IF ERRORLEVEL 1 ( ECHO To use this script you need to have Python installed & goto :eof ) ELSE ( python -x "%~f0" %* & goto :eof )

import os
import sys
import json
import urllib
import tempfile
import tarfile
from subprocess import Popen
from _winreg import OpenKey, CloseKey, QueryValueEx, SetValueEx, \
                   HKEY_CURRENT_USER, KEY_ALL_ACCESS, REG_EXPAND_SZ
import ctypes
from ctypes.wintypes import HWND, UINT, WPARAM, LPARAM, LPVOID


VENV_URL = "https://pypi.python.org/pypi/virtualenv/json"
APPDATA = os.environ['LocalAppData']
APP = 'lektor-cli'
LIB = 'lib'
ROOT_KEY = HKEY_CURRENT_USER
SUB_KEY = 'Environment'
LRESULT = LPARAM
HWND_BROADCAST = 0xFFFF
WM_SETTINGCHANGE = 0x1A

def find_location():
   install_dir = os.path.join(APPDATA, APP)
   if os.path.exists(install_dir) and os.path.isdir(install_dir):
       return None, None
   return install_dir, os.path.join(install_dir, LIB)

def fail(message):
   print 'Error: %s' % message
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

def install(virtualenv_url, virtualenv_filename, install_dir, lib_dir):
   t = tempfile.mkdtemp()
   with open(os.path.join(t, 'virtualenv.tar.gz'), 'wb') as f:
       download = urllib.urlopen(virtualenv_url)
       f.write(download.read())
       download.close()
   with tarfile.open(os.path.join(t, 'virtualenv.tar.gz'), 'r:gz') as tar:
       tar.extractall(path=t)

   os.makedirs(install_dir)
   os.makedirs(lib_dir)

   Popen(['python', 'virtualenv.py', lib_dir],
           cwd=os.path.join(t, virtualenv_filename)).wait()
   scripts = os.path.join(lib_dir, 'Scripts')
   #just using pip.exe and cwd will still install globally
   Popen([os.path.join(scripts, 'pip.exe'),
           'install', '--upgrade', 'git+https://github.com/lektor/lektor'],
           cwd=scripts).wait()

   with open(os.path.join(install_dir, 'lektor.cmd'), 'w') as link_file:
       link_file.write('@echo off\n')
       link_file.write('\"' + os.path.join(scripts, 'lektor.exe') + '\"' + ' %*')

   add_to_path(install_dir)


def main():
   print 'Welcome to Lektor'
   print
   print 'This script will install Lektor on your computer.'
   print

   install_dir, lib_dir = find_location()
   if install_dir == None:
       fail('Lektor seems to be installed already.')

   print '   Installing at: %s' % install_dir
   while 1:
       input = raw_input('Continue? [Yn] ').lower().strip()
       if input in ('', 'y'):
           break
       elif input == 'n':
           print 'Aborted!'
           sys.exit()

   for url in json.load(urllib.urlopen(VENV_URL))['urls']:
       if url['python_version'] == 'source':
           virtualenv_url = url['url']
           #stripping '.tar.gz'
           virtualenv_filename = url['filename'][:-7]
           break
   else:
       fail('Could not find virtualenv')

   install(virtualenv_url, virtualenv_filename, install_dir, lib_dir)

   print
   print 'All done!'

main()
