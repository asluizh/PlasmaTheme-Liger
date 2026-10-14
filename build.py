#!/usr/bin/env python3
"""Build every Liger component into ./build (see PROGRESS.md).

  python3 build.py                  wipe ./build, then build Liger and DarkLiger
  python3 build.py --variant dark   build one variant only (no wipe)
"""
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'build')
VARIANTS = ('light', 'dark')


def build_variant():
    sys.path.insert(0, os.path.join(HERE, 'generator'))
    import palette as P
    import plasma_style, colorscheme, aurorae, kvantum, lookandfeel
    print('[%s]' % P.THEME_NAME)
    print('  plasma style  ->', plasma_style.build(OUT))
    print('  color scheme  ->', colorscheme.build(OUT))
    print('  aurorae       ->', aurorae.build(OUT))
    print('  kvantum       ->', kvantum.build(OUT))
    print('  look-and-feel ->', lookandfeel.build(OUT))


def main():
    if '--variant' in sys.argv:
        os.environ['LIGER_VARIANT'] = sys.argv[sys.argv.index('--variant') + 1]
        build_variant()
        return
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    # one process per variant: the generators read the palette at import time
    for v in VARIANTS:
        subprocess.run([sys.executable, os.path.abspath(__file__), '--variant', v], check=True)


if __name__ == '__main__':
    main()
