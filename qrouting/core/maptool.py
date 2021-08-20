from PyQt5.QtCore import pyqtSignal, QEvent
from qgis.PyQt.QtGui import QIcon
from PyQt5.QtGui import QCursor
from typing import Type
from qgis.gui import QgsMapToolEmitPoint, QgsMapMouseEvent
from qgis.core import QgsCoordinateTransform
from ..util.util import to_wgs84

CUSTOM_CURSOR = QCursor(
    QIcon(":images/themes/default/cursors/mCapturePoint.svg").pixmap(16, 16)
)


class PointTool(QgsMapToolEmitPoint):
    def __init__(self, canvas):
        """
        :param canvas: current map canvas
        :type canvas: QgsMapCanvas
        """
        self.canvas = canvas
        QgsMapToolEmitPoint.__init__(self, self.canvas)

        self.crsSrc = self.canvas.mapSettings().destinationCrs()
        self.previous_point = None
        self.points = []
        self.reset()

    def reset(self) -> None:
        """reset captured points."""
        self.points = []

    canvasClicked = pyqtSignal(["QgsPointXY", int])

    def canvasReleaseEvent(self, event: QgsMapMouseEvent) -> None:
        # Get the click and emit a transformed point
        new_point = to_wgs84(
            event.mapPoint(),
            self.crsSrc,
            QgsCoordinateTransform.ForwardTransform,
        )
        # list_point = self.toMapCoordinates(new_point)
        self.points.append(new_point)
        self.canvasClicked.emit(new_point, self.points.index(new_point))

    doubleClicked = pyqtSignal()

    def canvasDoubleClickEvent(self, e: Type[QEvent]) -> None:
        """Ends point adding and deletes markers from map canvas."""
        self.doubleClicked.emit()

    def deactivate(self) -> None:
        super(PointTool, self).deactivate()
        self.deactivated.emit()
