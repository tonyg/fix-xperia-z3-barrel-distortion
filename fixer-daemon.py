#!/usr/bin/env python3
# To be run from daemontools
# See https://forum.xda-developers.com/z3/help/cm12-camera-distortion-t3060606/page2, which says:
# convert input.jpg -distort barrel '0.0132 -0.07765 0.14683' output.jpg.

import glob
import time
import os
import subprocess
import sys

def poll_wonky():
    for sourcename in glob.glob('Wonky/*'):
        leafname = os.path.split(sourcename)[1]
        targetname = os.path.join('Fixed', 'fixed_' + leafname)
        if not os.path.exists(targetname):
            sys.stdout.write('Converting %s...' % (leafname,))
            sys.stdout.flush()
            result = subprocess.run(['convert',
                                     sourcename,
                                     '-distort', 'barrel', '0.0132 -0.07765 0.14683',
                                     targetname])
            if result.returncode == 0:
                sys.stdout.write('OK')
                os.unlink(sourcename)
            else:
                sys.stdout.write(repr(result))
                os.rename(sourcename, os.path.join('Problems', leafname))
            sys.stdout.write('\n')
            sys.stdout.flush()

def main():
    while True:
        poll_wonky()
        time.sleep(5)

if __name__ == '__main__':
    main()
