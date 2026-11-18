// Plasma Style widget sheet, rendered by tools/plasmawidgets.py
import QtQuick
import QtQuick.Layouts
import org.kde.ksvg as KSvg
import org.kde.kirigami as Kirigami
import org.kde.plasma.core as PlasmaCore
import org.kde.plasma.components as PC3

Rectangle {
    id: root
    width: 620; height: 720
    color: Kirigami.Theme.backgroundColor
    Kirigami.Theme.colorSet: Kirigami.Theme.Window
    Kirigami.Theme.inherit: false

    // plasma-pa's VolumeSlider background: the live peak meter is a second
    // groove-highlight drawn with status Selected on top of the volume fill
    component VolumeSlider: PC3.Slider {
        id: control
        property real meterLevel: 0.6
        from: 0; to: 100
        background: KSvg.FrameSvgItem {
            imagePath: "widgets/slider"
            prefix: "groove"
            implicitWidth: Kirigami.Units.gridUnit * 12
            implicitHeight: fixedMargins.top + fixedMargins.bottom
            width: Math.max(fixedMargins.left + fixedMargins.right, control.availableWidth)
            height: implicitHeight
            x: control.leftPadding
            y: control.topPadding + Math.round((control.availableHeight - height) / 2)
            KSvg.FrameSvgItem {
                imagePath: "widgets/slider"
                prefix: "groove-highlight"
                anchors.left: parent.left; anchors.bottom: parent.bottom
                width: Math.max(fixedMargins.left + fixedMargins.right, Math.round(control.position * (control.availableWidth - control.handle.width / 2) + (control.handle.width / 2)))
                height: parent.height
            }
            KSvg.FrameSvgItem {
                imagePath: "widgets/slider"
                prefix: "groove-highlight"
                status: KSvg.FrameSvgItem.Selected
                anchors.left: parent.left; anchors.bottom: parent.bottom
                width: Math.max(fixedMargins.left + fixedMargins.right, Math.round(control.meterLevel * control.position * control.availableWidth))
                height: parent.height
            }
        }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 10
        PC3.Label { text: "Switches" }
        RowLayout {
            spacing: 18
            PC3.Switch { text: "Off" }
            PC3.Switch { text: "On"; checked: true }
            PC3.Switch { text: "Disabled"; enabled: false }
            PC3.Switch { text: "Dis. on"; enabled: false; checked: true }
        }
        PC3.Label { text: "Volume (meter at 60% of the volume)" }
        VolumeSlider { Layout.fillWidth: true; value: 70 }
        VolumeSlider { Layout.fillWidth: true; value: 35; meterLevel: 0.9 }
        PC3.Label { text: "Slider / ProgressBar" }
        PC3.Slider { Layout.fillWidth: true; from: 0; to: 100; value: 40 }
        PC3.ProgressBar { Layout.fillWidth: true; from: 0; to: 100; value: 65 }
        PC3.ProgressBar { Layout.fillWidth: true; from: 0; to: 100; value: 3 }
        PC3.ProgressBar { Layout.fillWidth: true; indeterminate: true }
        PC3.Label { text: "Dock tasks: launcher, normal, minimized, active, attention, then hovered" }
        Item {
            Layout.preferredWidth: dock.width; Layout.preferredHeight: dock.height
            KSvg.FrameSvgItem {
                id: dock
                imagePath: "widgets/panel-background"
                prefix: "south"
                width: taskRow.width + 20; height: 64
                Row {
                    id: taskRow
                    x: 10; y: 8
                    Repeater {
                        model: ["", "normal", "minimized", "focus", "attention",
                                "launcher-hover", "normal-hover", "minimized-hover", "focus-hover", "attention-hover"]
                        KSvg.FrameSvgItem {
                            imagePath: "widgets/tasks"
                            prefix: modelData === "" ? "launcher" : ["south-" + modelData, modelData]
                            width: 52; height: 52
                            Kirigami.Icon { source: "system-file-manager"; anchors.centerIn: parent; anchors.verticalCenterOffset: -2; width: 36; height: 36 }
                        }
                    }
                }
            }
            Column {
                x: dock.width + 16; y: -40
                Repeater {
                    model: ["normal", "focus-hover", "focus"]
                    KSvg.FrameSvgItem {
                        imagePath: "widgets/tasks"
                        prefix: ["west-" + modelData, modelData]
                        width: 52; height: 46
                        Kirigami.Icon { source: "system-file-manager"; anchors.centerIn: parent; width: 32; height: 32 }
                    }
                }
            }
        }
        PC3.Label { text: "Check / radio / buttons" }
        RowLayout {
            PC3.CheckBox { text: "Check"; checked: true }
            PC3.RadioButton { text: "Radio"; checked: true }
            PC3.Button { text: "Button" }
            PC3.ToolButton { icon.name: "audio-volume-high"; checkable: true; checked: true }
        }
    }
}
