"""
Liger Global Theme (look-and-feel package).

Ties the parts together and provides an Aqua desktop layout:
  * top:    22-26px menu bar  (launcher, global menu, spacer, tray, clock)
  * bottom: floating, fit-to-content 2D dock (icon-only task manager)
"""
import json
import os

import palette as P

LAF_ID = 'org.kde.liger.desktop'

DEFAULTS = """[kdeglobals][General]
ColorScheme={id}

[kdeglobals][KDE]
widgetStyle=kvantum

[plasmarc][Theme]
name={id}

[kwinrc][org.kde.kdecoration2]
library=org.kde.kwin.aurorae.v2
theme=__aurorae__svg__{id}
ButtonsOnLeft=XIA
ButtonsOnRight=SF

[kcminputrc][Mouse]
cursorTheme=breeze_cursors
"""

LAYOUT_JS = r"""// Liger: Aqua desktop layout (menu bar + 2D dock)
var menubar = new Panel;
menubar.location = "top";
menubar.height = Math.max(24, Math.round(gridUnit * 1.35));
menubar.floating = false;
menubar.hiding = "none";

var launcher = menubar.addWidget("org.kde.plasma.kickoff");
launcher.currentConfigGroup = ["General"];
launcher.writeConfig("icon", "start-here-kde-symbolic");
menubar.addWidget("org.kde.plasma.appmenu");
menubar.addWidget("org.kde.plasma.panelspacer");
menubar.addWidget("org.kde.plasma.systemtray");
var clock = menubar.addWidget("org.kde.plasma.digitalclock");
clock.currentConfigGroup = ["Appearance"];
clock.writeConfig("showDate", "false");
clock.writeConfig("use24hFormat", "2");

var dock = new Panel;
dock.location = "bottom";
dock.height = 2 * Math.ceil(gridUnit * 3 / 2);
dock.floating = true;
dock.lengthMode = "fit";
dock.alignment = "center";
dock.hiding = "none";

var tasks = dock.addWidget("org.kde.plasma.icontasks");
tasks.currentConfigGroup = ["General"];
tasks.writeConfig("launchers", ["applications:org.kde.dolphin.desktop", "applications:org.kde.konsole.desktop", "applications:org.kde.kate.desktop", "applications:systemsettings.desktop"]);
tasks.writeConfig("iconSpacing", "1");
tasks.writeConfig("maxStripes", "1");
dock.addWidget("org.kde.plasma.marginsseparator");
dock.addWidget("org.kde.plasma.trash");
"""


def build(out):
    root = os.path.join(out, 'plasma', 'look-and-feel', LAF_ID)
    contents = os.path.join(root, 'contents')
    os.makedirs(os.path.join(contents, 'layouts'), exist_ok=True)
    meta = {
        "KPackageStructure": "Plasma/LookAndFeel",
        "KPlugin": {
            "Authors": [{"Name": P.AUTHOR}],
            "Category": "",
            "Description": "Aqua, the lickable way: Snow Leopard to Mavericks",
            "Id": LAF_ID,
            "License": "GPL-3.0-or-later",
            "Name": P.THEME_NAME,
            "Version": P.VERSION,
        },
        "X-Plasma-APIVersion": "2",
    }
    with open(os.path.join(root, 'metadata.json'), 'w') as fh:
        json.dump(meta, fh, indent=4)
    with open(os.path.join(contents, 'defaults'), 'w') as fh:
        fh.write(DEFAULTS.format(id=P.THEME_ID))
    with open(os.path.join(contents, 'layouts', 'org.kde.plasma.desktop-layout.js'), 'w') as fh:
        fh.write(LAYOUT_JS)
    return root
