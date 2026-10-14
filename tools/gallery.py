#!/usr/bin/env python3
"""Widget gallery used to eyeball the Kvantum theme (run inside tools/testsession.sh)."""
import sys

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDialogButtonBox, QGridLayout, QGroupBox,
                               QHBoxLayout, QLabel, QLineEdit, QListWidget, QMainWindow, QProgressBar,
                               QPushButton, QRadioButton, QSlider, QSpinBox, QTabWidget, QToolBar, QTreeWidget,
                               QTreeWidgetItem, QVBoxLayout, QWidget)


def main():
    app = QApplication(sys.argv)
    w = QMainWindow()
    w.setWindowTitle('Liger — widget gallery')
    tb = QToolBar('Main')
    for t in ('Back', 'Forward', 'Share'):
        a = tb.addAction(t)
    a.setCheckable(True)
    a.setChecked(True)
    w.addToolBar(tb)
    mb = w.menuBar()
    for m in ('File', 'Edit', 'View', 'Window', 'Help'):
        menu = mb.addMenu(m)
        menu.addAction('New')
        menu.addAction('Open…')
        menu.addSeparator()
        c = menu.addAction('Checkable')
        c.setCheckable(True)
        c.setChecked(True)

    central = QWidget()
    g = QGridLayout(central)

    box = QGroupBox('Buttons')
    v = QVBoxLayout(box)
    row = QHBoxLayout()
    row.addWidget(QPushButton('Cancel'))
    ok = QPushButton('OK')
    ok.setDefault(True)
    row.addWidget(ok)
    t = QPushButton('Toggle')
    t.setCheckable(True)
    t.setChecked(True)
    row.addWidget(t)
    d = QPushButton('Disabled')
    d.setEnabled(False)
    row.addWidget(d)
    v.addLayout(row)
    combo = QComboBox()
    combo.addItems(['Snow Leopard', 'Lion', 'Mountain Lion', 'Mavericks'])
    v.addWidget(combo)
    ec = QComboBox()
    ec.setEditable(True)
    ec.addItems(['Editable'])
    v.addWidget(ec)
    v.addWidget(QLineEdit('Text field'))
    sp = QSpinBox()
    sp.setValue(42)
    v.addWidget(sp)
    g.addWidget(box, 0, 0)

    box2 = QGroupBox('Choices')
    v2 = QVBoxLayout(box2)
    c1 = QCheckBox('Checked')
    c1.setChecked(True)
    v2.addWidget(c1)
    v2.addWidget(QCheckBox('Unchecked'))
    c3 = QCheckBox('Tristate')
    c3.setTristate(True)
    c3.setCheckState(Qt.PartiallyChecked)
    v2.addWidget(c3)
    r1 = QRadioButton('Radio on')
    r1.setChecked(True)
    v2.addWidget(r1)
    v2.addWidget(QRadioButton('Radio off'))
    s = QSlider(Qt.Horizontal)
    s.setValue(60)
    v2.addWidget(s)
    pb = QProgressBar()
    pb.setValue(65)
    v2.addWidget(pb)
    g.addWidget(box2, 0, 1)

    tabs = QTabWidget()
    lst = QListWidget()
    for i in range(30):
        lst.addItem('Item %d' % i)
    lst.setAlternatingRowColors(True)
    lst.setCurrentRow(2)
    tabs.addTab(lst, 'List')
    tree = QTreeWidget()
    tree.setHeaderLabels(['Name', 'Size', 'Kind'])
    tree.setAlternatingRowColors(True)
    for i in range(20):
        QTreeWidgetItem(tree, ['File %d' % i, '%d KB' % (i * 3), 'Document'])
    tree.sortByColumn(0, Qt.AscendingOrder)
    tree.setSortingEnabled(True)
    tabs.addTab(tree, 'Tree')
    tabs.addTab(QLabel('Third'), 'Other')
    tabs.setCurrentIndex(1)
    g.addWidget(tabs, 1, 0, 1, 2)

    bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
    g.addWidget(bb, 2, 0, 1, 2)
    w.setCentralWidget(central)
    w.resize(760, 640)
    w.show()
    if '--menu' in sys.argv:
        # Wayland refuses popups without an input serial, so embed the menu in a plain window
        from PySide6.QtWidgets import QMenu
        holder = QWidget()
        holder.setWindowTitle('Menu preview')
        lay = QVBoxLayout(holder)
        ctx = QMenu(holder)
        ctx.setWindowFlags(Qt.Widget)
        ctx.addAction('Open')
        ctx.addAction('Get Info')
        dis = ctx.addAction('Disabled item')
        dis.setEnabled(False)
        ctx.addSeparator()
        chk = ctx.addAction('Show Path Bar')
        chk.setCheckable(True)
        chk.setChecked(True)
        sub = ctx.addMenu('Arrange By')
        sub.addAction('Name')
        ctx.addAction('Move to Trash')
        ctx.setActiveAction(ctx.actions()[1])
        lay.addWidget(ctx)
        holder._keep = ctx
        holder.resize(260, 240)
        holder.show()
        w._holder = holder
    if '--popup' in sys.argv:
        # real popup (works under X11/XWayland: QT_QPA_PLATFORM=xcb)
        from PySide6.QtWidgets import QMenu
        pm = QMenu(w)
        for t in ('Open', 'Get Info', 'Duplicate'):
            pm.addAction(t)
        d2 = pm.addAction('Disabled item')
        d2.setEnabled(False)
        pm.addSeparator()
        c2 = pm.addAction('Show Path Bar')
        c2.setCheckable(True)
        c2.setChecked(True)
        pm.addMenu('Arrange By').addAction('Name')
        pm.addAction('Move to Trash')
        QTimer.singleShot(3000, lambda: pm.popup(w.mapToGlobal(w.rect().center())))
        QTimer.singleShot(3300, lambda: pm.setActiveAction(pm.actions()[1]))
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
