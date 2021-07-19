from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QCursor, QPixmap
from PyQt5.QtWidgets import QApplication

from qgis.gui import QgsMapToolEmitPoint, QgsVertexMarker, QgsMapMouseEvent
from qgis.core import (QgsCoordinateReferenceSystem,
                       QgsCoordinateTransform,
                       QgsProject
                       )

WGS = QgsCoordinateReferenceSystem("EPSG:4326")


class PointTool(QgsMapToolEmitPoint):

    canvasClicked = pyqtSignal('QgsPointXY')

    def canvasReleaseEvent(self, event: QgsMapMouseEvent):
        # Get the click and emit a transformed point

        crs_canvas = self.canvas().mapSettings().destinationCrs()
        xformer = QgsCoordinateTransform(crs_canvas, WGS, QgsProject.instance())

        point_clicked = event.mapPoint()
        point_wgs = xformer.transform(point_clicked)

        self.canvasClicked.emit(point_wgs)