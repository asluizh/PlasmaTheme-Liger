#!/usr/bin/env python3
"""Build every Liger component into ./build (see PROGRESS.md)."""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'generator'))

import plasma_style, colorscheme  # noqa: E402

OUT = os.path.join(HERE, 'build')


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    print('plasma style  ->', plasma_style.build(OUT))
    print('color scheme  ->', colorscheme.build(OUT))
    try:
        import aurorae
        print('aurorae       ->', aurorae.build(OUT))
    except ImportError:
        pass
    try:
        import kvantum
        print('kvantum       ->', kvantum.build(OUT))
    except ImportError:
        pass
    try:
        import lookandfeel
        print('look-and-feel ->', lookandfeel.build(OUT))
    except ImportError:
        pass


if __name__ == '__main__':
    main()
