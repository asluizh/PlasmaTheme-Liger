#!/usr/bin/env python3
"""Render PlasmaComponents3 widgets with a built Liger Plasma Style, offscreen.

usage: tools/plasmawidgets.py [--theme Liger|DarkLiger] [-o out.png]
Uses private XDG dirs in .testsession-widgets/; run build.py first.
"""
import argparse
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--theme', default='Liger')
    ap.add_argument('-o', '--out', default=None)
    ap.add_argument('--child', action='store_true', help=argparse.SUPPRESS)
    a = ap.parse_args()
    out = os.path.abspath(a.out or os.path.join(HERE, 'build', 'widgets-%s.png' % a.theme))
    if not a.child:
        work = os.path.join(HERE, '.testsession-widgets')
        shutil.rmtree(work, ignore_errors=True)
        cfg, data = os.path.join(work, 'config'), os.path.join(work, 'data', 'plasma', 'desktoptheme')
        os.makedirs(cfg)
        os.makedirs(data)
        os.symlink(os.path.join(HERE, 'build', 'plasma', 'desktoptheme', a.theme), os.path.join(data, a.theme))
        with open(os.path.join(HERE, 'build', 'color-schemes', a.theme + '.colors')) as fh:
            colors = fh.read()
        with open(os.path.join(cfg, 'kdeglobals'), 'w') as fh:
            fh.write(colors + '\n[KDE]\nAnimationDurationFactor=0\n[Icons]\nTheme=breeze\n')
        with open(os.path.join(cfg, 'plasmarc'), 'w') as fh:
            fh.write('[Theme]\nname=%s\n' % a.theme)
        env = dict(os.environ, XDG_CONFIG_HOME=cfg, XDG_DATA_HOME=os.path.join(work, 'data'),
                   XDG_CACHE_HOME=os.path.join(work, 'cache'), QT_QPA_PLATFORM='offscreen',
                   QT_QUICK_CONTROLS_STYLE='org.kde.desktop')
        sys.exit(subprocess.call([sys.executable, __file__, '--child', '--theme', a.theme, '-o', out], env=env))

    from PySide6.QtCore import QTimer, QUrl
    from PySide6.QtGui import QGuiApplication
    from PySide6.QtQuick import QQuickView
    app = QGuiApplication(sys.argv)
    v = QQuickView()
    v.engine().addImportPath('/usr/lib64/qt6/qml')
    v.engine().addImportPath('/usr/lib/qt6/qml')
    v.setSource(QUrl.fromLocalFile(os.path.join(HERE, 'tools', 'plasmawidgets.qml')))
    for e in v.errors():
        print(e.toString(), file=sys.stderr)
    if v.status() != QQuickView.Status.Ready:
        sys.exit(1)
    v.show()

    def grab():
        v.grabWindow().save(out)
        print(out)
        app.quit()
    QTimer.singleShot(1500, grab)
    app.exec()


if __name__ == '__main__':
    main()
