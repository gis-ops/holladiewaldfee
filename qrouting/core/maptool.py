from PyQt5.QtCore import pyqtSignal
from qgis.PyQt.QtGui import QIcon
from PyQt5.QtGui import QCursor, QPixmap
from PyQt5.QtWidgets import QApplication

from qgis.gui import QgsMapToolEmitPoint, QgsVertexMarker, QgsMapMouseEvent
from qgis.core import (QgsCoordinateReferenceSystem,
                       QgsCoordinateTransform,
                       QgsProject
                       )
from ..util.util import maybe_transform_wgs84

CUSTOM_CURSOR = QCursor(
    QIcon(":images/themes/default/cursors/mCapturePoint.svg").pixmap(16, 16)
)


class PointTool(QgsMapToolEmitPoint):

    canvasClicked = pyqtSignal('QgsPointXY')

    def canvasReleaseEvent(self, event: QgsMapMouseEvent):
        # Get the click and emit a transformed point

        crs_canvas = self.canvas().mapSettings().destinationCrs()
        self.canvasClicked.emit(maybe_transform_wgs84(
            event.mapPoint(), crs_canvas, QgsCoordinateTransform.ForwardTransform
            )
        )

    def activate(self):
        super().activate()
        QApplication.setOverrideCursor(CUSTOM_CURSOR)
