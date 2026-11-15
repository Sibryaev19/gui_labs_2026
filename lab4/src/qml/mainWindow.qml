
import QtQuick 2.0
import QtQuick.Window 2.3

import "components"

Window {
    id: root
    visible: true
    width: 1000
    height: 1000
    title: "Paint!"

    Component.onCompleted: _backend.registerCanvas(canvas)

    Rectangle {
        id: tools
        width: parent.width
        height: 150
        color: "#545454"

        property color paintColor: "#33B5E5"
        property int thickness: 1
        property int spacing: 4

        Column {
            spacing: tools.spacing
            anchors.centerIn: parent

            Row {
                spacing: tools.spacing
                anchors.horizontalCenter: parent.horizontalCenter

                Repeater {
                    model: ["#33B5E5", "#99CC00", "#FFBB33", "#FF4444"]
                    Square {
                        active: tools.paintColor === color
                        color: modelData
                        onClicked: tools.paintColor = color
                    }
                }
            }

            Row {
                spacing: tools.spacing
                anchors.horizontalCenter: parent.horizontalCenter

                Repeater {
                    model: [1,2,3,4,5]

                    Circle {
                        id: circle
                        active: tools.thickness === thickness
                        thickness: modelData
                        text: thickness
                        onClicked: tools.thickness = thickness
                    }
                }
            }
        }

    }

    Canvas {
        id: canvas
        anchors {
            left: parent.left
            right: parent.right
            top: tools.bottom
            bottom: parent.bottom
            margins: 8
        }

        property real lastX
        property real lastY
        property color color: tools.paintColor
        property string restoreUrl: ""
        property string snapshotCache: ""

        onPaint: {
            var ctx = getContext("2d")

            if (restoreUrl !== "" && isImageLoaded(restoreUrl)) {
                ctx.drawImage(restoreUrl, 0, 0)
                snapshotCache = restoreUrl
                restoreUrl = ""
                lastX = paint_area.mouseX
                lastY = paint_area.mouseY
                return
            }

            ctx.lineWidth = tools.thickness
            ctx.strokeStyle = canvas.color
            ctx.beginPath()
            ctx.moveTo(lastX, lastY)

            lastX = paint_area.mouseX
            lastY = paint_area.mouseY

            ctx.lineTo(lastX, lastY)
            ctx.stroke()
        }

        onWidthChanged: redrawSnapshot()
        onHeightChanged: redrawSnapshot()

        function redrawSnapshot() {
            if (snapshotCache !== "" && restoreUrl === "") {
                restoreUrl = snapshotCache
                loadImage(restoreUrl)
            }
        }

        onImageLoaded: requestPaint()

        Component.onCompleted: {
            var data_url = _backend.loadSnapshot()
            if (data_url !== "") {
                restoreUrl = data_url
                loadImage(data_url)
            }
        }

        MouseArea {
            id: paint_area
            anchors.fill: parent

            onPressed: {
                canvas.lastX = mouseX
                canvas.lastY = mouseY
            }

            onPositionChanged: {
                canvas.requestPaint()
            }

            onReleased: {
                canvas.snapshotCache = canvas.toDataURL("image/png")
            }
        }

        function snapshot() {
            _backend.receiveSnapshot(canvas.toDataURL("image/png"))
        }
    }
}
