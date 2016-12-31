#!/usr/bin/env python3
# To be run from daemontools
# See https://forum.xda-developers.com/z3/help/cm12-camera-distortion-t3060606/page2, which says:
# convert input.jpg -distort barrel '0.0132 -0.07765 0.14683' output.jpg.

import glob
import time
import os
import subprocess
import sys

# ensure_dir(PathString) -> None
# Creates all directories in path `p`, including intermediate directories.
# Example: ensure_dir('a/b/c') -- creates a, a/b, and a/b/c as directories.
def ensure_dir(p):
    try:
        os.makedirs(p)
    except FileExistsError:
        return
    sys.stdout.write('Created dir %s\n' % (p,))
    sys.stdout.flush()

# clean_dirs(PathString, PathString) -> None
# Removes path `p` and all parent directories until a remove fails OR
# until `p` is a prefix of `stop_at`. Analogous to `os.removedirs`,
# except has `stop_at`.
# Example: clean_dirs('a/b/c/d', 'a/b') -- removes a/b/c/d and a/b/c,
# but only if both are otherwise empty.
def clean_dirs(p, stop_at):
    while not stop_at.startswith(p):
        try:
            os.rmdir(p)
        except OSError:
            return
        sys.stdout.write('Removed dir %s\n' % (p,))
        sys.stdout.flush()
        p = os.path.dirname(p) # change `p` from `.../a/b` to `.../a`, e.g.

# poll_wonky() -> None
# Main routine: checks and processes the contents of the `Wonky/` subdir.
def poll_wonky():
    for (sourcedir, _subdirs, leafnames) in os.walk('Wonky'):
        subdirparts = sourcedir.split('/')[1:] # If sourcedir is `a/b/c`, subdirparts is ['b', 'c']
        inprogressdir = os.path.join('Inprogress', *subdirparts) # ... and inprogressdir is 'Inprogress/b/c'
        problemsdir = os.path.join('Problems', *subdirparts) # ... likewise
        targetdir = os.path.join('Fixed', *subdirparts) # ... likewise

        should_clean_dirs = len(subdirparts) and len(leafnames)

        if len(subdirparts): ensure_dir(inprogressdir)

        for leafname in leafnames:
            sourcefile = os.path.join(sourcedir, leafname)
            inprogressfile = os.path.join(inprogressdir, 'fixed_' + leafname)
            targetfile = os.path.join(targetdir, 'fixed_' + leafname)
            sys.stdout.write('Converting %s...' % (sourcefile,))
            sys.stdout.flush()
            success = False
            if os.path.exists(targetfile):
                result = 'Target file exists'
            else:
                result = subprocess.run(['convert',
                                         sourcefile,
                                         '-distort', 'barrel', '0.0132 -0.07765 0.14683',
                                         inprogressfile])
                if result.returncode == 0:
                    success = True
            if success:
                sys.stdout.write('OK')
                os.unlink(sourcefile)
            else:
                sys.stdout.write(repr(result))
                if len(subdirparts): ensure_dir(problemsdir)
                os.rename(sourcefile, os.path.join(problemsdir, leafname))
            sys.stdout.write('\n')
            sys.stdout.flush()
        if should_clean_dirs: clean_dirs(sourcedir, 'Wonky')

        if len(subdirparts): ensure_dir(targetdir)
        for leafname in leafnames:
            inprogressfile = os.path.join(inprogressdir, 'fixed_' + leafname)
            targetfile = os.path.join(targetdir, 'fixed_' + leafname)
            if os.path.exists(inprogressfile):
                os.rename(inprogressfile, targetfile)

        if should_clean_dirs: clean_dirs(inprogressdir, 'Inprogress')

# main() -> None
# Entry point. Repeatedly calls `poll_wonky`, with a 5 second delay in between calls.
def main():
    sys.stdout.write('Starting up.\n')
    sys.stdout.flush()
    while True:
        poll_wonky()
        time.sleep(5)

if __name__ == '__main__':
    main()
