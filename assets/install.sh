#!/bin/sh
# This script helps you install Lektor on your computer.  Right now it
# only supports Linux and OS X and only on OS X will it install the
# desktop version.
#
# For more information see https://www.getlektor.com/

# Wrap everything in a function so that we do not accidentally execute
# something we should not in case a truncated version of the script
# is executed.
I() {
  set -u

  if ! hash python 2> /dev/null; then
    echo "Error: To use this script you need to have Python installed"
    exit 1
  fi

  python - <<'EOF'
if 1:

    import os
    import sys
    import json
    import tempfile
    import shutil
    from subprocess import Popen
    try:
        from urllib.request import urlopen
    except ImportError:
        from urllib import urlopen

    PY2 = sys.version_info[0] == 2
    if PY2:
        input = raw_input

    sys.stdin = open('/dev/tty', 'r')

    VENV_URL = "https://pypi.python.org/pypi/virtualenv/json"
    KNOWN_BINS = ['/usr/local/bin', '/opt/local/bin',
                  os.path.join(os.environ['HOME'], '.bin'),
                  os.path.join(os.environ['HOME'], '.local', 'bin')]

    def find_user_paths():
        rv = []
        for item in os.environ['PATH'].split(':'):
            if os.access(item, os.W_OK) \
               and item not in rv \
               and '/sbin' not in item:
                rv.append(item)
        return rv

    def bin_sort_key(path):
        try:
            return KNOWN_BINS.index(path)
        except ValueError:
            return float('inf')

    def find_locations(paths):
        paths.sort(key=bin_sort_key)
        for path in paths:
            if path.startswith(os.environ['HOME']):
                return path, os.path.join(os.environ['HOME'],
                    '.local', 'lib', 'lektor')
            elif path.endswith('/bin'):
                return path, os.path.join(
                    os.path.dirname(path), 'lib', 'lektor')
        None, None

    def get_confirmation():
        while 1:
            user_input = input('Continue? [Yn] ').lower().strip()
            if user_input in ('', 'y'):
                break
            elif user_input == 'n':
                print()
                print('Aborted!')
                sys.exit()

    def deletion_error(func, path, excinfo):
        print('Problem deleting {}'.format(path))
        print('Please try and delete {} manually'.format(path))
        print('Aborted!')
        sys.exit()

    def wipe_installation(lib_dir, symlink_path):
        if os.path.lexists(symlink_path):
            os.remove(symlink_path)
        if os.path.exists(lib_dir):
            shutil.rmtree(lib_dir, onerror=deletion_error)

    def check_installation(lib_dir, bin_dir):
        symlink_path = os.path.join(bin_dir, 'lektor')
        if os.path.exists(lib_dir) or os.path.lexists(symlink_path):
            print('   Lektor seems to be installed already.')
            print('   Continuing will delete:')
            print('   %s' % lib_dir)
            print('   and remove this symlink:')
            print('   %s' % symlink_path)
            print()
            get_confirmation()
            print()
            wipe_installation(lib_dir, symlink_path)

    def fail(message):
        print('Error: %s' % message)
        sys.exit(1)

    def install(virtualenv_url, lib_dir, bin_dir):
        t = tempfile.mkdtemp()
        Popen('curl -sf "%s" | tar -xzf - --strip-components=1' %
              virtualenv_url, shell=True, cwd=t).wait()

        try:
            os.makedirs(lib_dir)
        except OSError:
            pass
        Popen([sys.executable, './virtualenv.py', lib_dir], cwd=t).wait()
        Popen([os.path.join(lib_dir, 'bin', 'pip'),
           'install', '--upgrade', 'Lektor']).wait()
        os.symlink(os.path.join(lib_dir, 'bin', 'lektor'),
                   os.path.join(bin_dir, 'lektor'))

    def main():
        print()
        print('Welcome to Lektor')
        print()
        print('This script will install Lektor on your computer.')
        print()

        paths = find_user_paths()
        if not paths:
            fail('None of the items in $PATH are writable. Run with '
                 'sudo or add a $PATH item that you have access to.')

        bin_dir, lib_dir = find_locations(paths)
        if bin_dir is None or lib_dir is None:
            fail('Could not determine installation location for Lektor.')

        check_installation(lib_dir, bin_dir)

        print('Installing at:')
        print('  bin: %s' % bin_dir)
        print('  app: %s' % lib_dir)
        print()

        get_confirmation()

        for url in json.loads(urlopen(VENV_URL).read().decode('utf-8'))['urls']:
            if url['python_version'] == 'source':
                virtualenv = url['url']
                break
        else:
            fail('Could not find virtualenv')

        install(virtualenv, lib_dir, bin_dir)

        print()
        print('All done!')

    main()
EOF
}

I
