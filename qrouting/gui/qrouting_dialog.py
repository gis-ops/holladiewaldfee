# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QRoutingDialog
                                 A QGIS plugin
 t
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2021-07-09
        git sha              : $Format:%H$
        copyright            : (C) 2021 by Chris
        email                : test
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from qgis.PyQt import QtWidgets
from qgis.PyQt.QtGui import QIcon, QTextDocument
from qgis.gui import QgisInterface, QgsMapTool, QgsMapCanvasAnnotationItem
from PyQt5.QtWidgets import QApplication

import os.path
import sys
from typing import List, Union
from qgis.core import (
                        QgsProject,
                        QgsCoordinateTransform,
                        QgsPointXY,
                        QgsVectorLayer,
                        QgsLineString,
                        QgsFeature,
                        QgsRectangle,
                        QgsPoint,
                        QgsGeometry,
                        QgsTextAnnotation
                        )
from qgis.PyQt.QtWidgets import QMessageBox, QComboBox
from qgis.PyQt.QtCore import QSizeF, QPointF

from ..ui.qrouting_dialog_base_ui import Ui_QRoutingDialogBase
from ..core.maptool import PointTool
from ..util.util import to_wgs84
from ..util.resources import _locate_resource
from ..core.client import QClient
from ..core.routing import _get_profile_from_button_name
from ..core.exceptions import InsufficientPoints

current_dir = os.path.dirname(os.path.abspath(__file__))
rp_path = os.path.join(current_dir, "../third_party", "routing-py")
sys.path.append(rp_path)
from routingpy import get_router_by_name
from routingpy.direction import Direction
from routingpy.routers import Valhalla


class QRoutingDialog(QtWidgets.QDialog, Ui_QRoutingDialogBase):
    def __init__(self, iface: QgisInterface, parent=None):
        """Constructor."""
        super(QRoutingDialog, self).__init__(parent)
        self.setupUi(self)
        self.iface = iface
        self.project = QgsProject.instance()
        self.annotations = []
        self.point_tool = PointTool(iface.mapCanvas())
        self.last_map_tool: QgsMapTool = None
        self.selected_provider = self.provider.currentText()
        self.set_icons()

        self.waypoint_widget.add_wp.clicked.connect(self._on_point_tool_init)
        self.waypoint_widget.remove_wp.clicked.connect(self.waypoint_widget.clear_table)

        self.waypoint_widget.move_up.clicked.connect(self.waypoint_widget.move_item_up)
        self.waypoint_widget.move_down.clicked.connect(self.waypoint_widget.move_item_down)
        self.waypoint_widget.add_from_layer.clicked.connect(self.waypoint_widget.open_layer_selection)
        self.waypoint_widget.layer_added.connect(self.check_provider)
        self.waypoint_widget.point_added.connect(self.check_provider)

        self.provider.currentTextChanged.connect(self.on_provider_change)
        self.finished.connect(self.run)

    def run(self, result: int) -> None:
        """Run main functionality after pressing OK."""
        if result:
            locations = self.get_locations_from_table()
            selected_method = self.provider.currentText()
            selected_profile = self.get_profile(self.selected_provider)
            directions = self.get_directions(self.selected_provider,
                                             selected_profile,
                                             selected_method,
                                             locations
                                             )

            self.add_result_layer(self.selected_provider, selected_profile, directions)

    def _zoom_to_extent(self, layer: QgsVectorLayer, project: QgsProject) -> None:
        """Zoom to the extent of a layer."""
        ext = layer.extent()
        _bbox = []
        min_y, max_x, max_y, min_x = ext.yMinimum(), ext.xMaximum(), ext.yMaximum(), ext.xMinimum()
        for p in [QgsPointXY(min_x, min_y), QgsPointXY(max_x, max_y)]:
            p = to_wgs84(
                        p,
                        project.crs(),
                        QgsCoordinateTransform.ReverseTransform,
                    )
            _bbox.append(p)

        self.iface.mapCanvas().zoomToFeatureExtent(
            QgsRectangle(*_bbox)
        )

    def _on_point_tool_init(self) -> None:
        self.hide()
        self.waypoint_widget.coord_table.setRowCount(0)
        self._clear_annotations()
        self.last_maptool = self.iface.mapCanvas().mapTool()
        self.point_tool = PointTool(self.iface.mapCanvas())
        self.iface.mapCanvas().setMapTool(self.point_tool)
        self.point_tool.canvasClicked.connect(self._on_map_click)
        self.point_tool.doubleClicked.connect(self._on_map_doubleclick)

    def _on_map_click(self, point: QgsPointXY, idx: int) -> None:
        self.waypoint_widget.add_to_table(point)
        annotation_point = to_wgs84(point, self.project.crs(), QgsCoordinateTransform.ReverseTransform)

        annotation = self._point_tool_annotate_point(annotation_point, idx)
        self.annotations.append(annotation)
        self.project.annotationManager().addAnnotation(annotation)

    def _on_map_doubleclick(self):
        self.point_tool.canvasClicked.disconnect()
        self.point_tool.doubleClicked.disconnect()
        QApplication.restoreOverrideCursor()
        self.show()
        self.iface.mapCanvas().setMapTool(self.last_maptool)

    def _point_tool_annotate_point(self, point, idx):
        annotation = QgsTextAnnotation()

        c = QTextDocument()
        html = "<strong>" + str(idx) + "</strong>"
        c.setHtml(html)

        annotation.setDocument(c)

        annotation.setFrameSizeMm(QSizeF(5, 8))
        annotation.setFrameOffsetFromReferencePointMm(QPointF(5, 5))
        annotation.setMapPosition(point)
        annotation.setMapPositionCrs(self.iface.mapCanvas().mapSettings().destinationCrs())

        return QgsMapCanvasAnnotationItem(annotation, self.iface.mapCanvas()).annotation()

    def set_icons(self) -> None:
        # default QGIS icons
        add_point_icon = QIcon(":images/themes/default/symbologyAdd.svg")
        remove_points_icon = QIcon(":images/themes/default/mActionRemove.svg")
        add_layer_icon = QIcon(":images/themes/default/mActionAddLayer.svg")
        arrow_up_icon = QIcon(":images/themes/default/mActionArrowUp.svg")
        arrow_down_icon = QIcon(":images/themes/default/mActionArrowDown.svg")
        self.waypoint_widget.add_wp.setIcon(add_point_icon)
        self.waypoint_widget.remove_wp.setIcon(remove_points_icon)
        self.waypoint_widget.add_from_layer.setIcon(add_layer_icon)
        self.waypoint_widget.move_up.setIcon(arrow_up_icon)
        self.waypoint_widget.move_down.setIcon(arrow_down_icon)

        # custom icons
        self.profile_widget.profile_ped.setIcon(QIcon(_locate_resource("pedestrian.svg")))
        self.profile_widget.profile_mbike.setIcon(QIcon(_locate_resource("motorbike.svg")))
        self.profile_widget.profile_car.setIcon(QIcon(_locate_resource("car.svg")))
        self.profile_widget.profile_bike.setIcon(QIcon(_locate_resource("bike.svg")))
        self.profile_widget.profile_bus.setIcon(QIcon(_locate_resource("bus.svg")))

    def get_profile(self, provider: str) -> str:
        for button in self.profile_widget.profile_buttons:
            if button.isChecked():
                button_name = button.objectName()
                return _get_profile_from_button_name(button_name, provider)

    def get_locations_from_table(self) -> Union[None, List[List[float]]]:
        rows = self.waypoint_widget.coord_table.rowCount()
        locations = []
        try:
            for row in range(rows):
                lat, lon = (
                    self.waypoint_widget.coord_table.item(row, 0),
                    self.waypoint_widget.coord_table.item(row, 1),
                                          )
                location = {"lat": float(lat.text()), "lon": float(lon.text())}
                widget = self.waypoint_widget.coord_table.cellWidget(row, 2)
                if widget.isEnabled():
                    location.update({"type": widget.currentText()})

                locations.append(location)

        except Exception as e:
            QMessageBox.critical(self.iface.mainWindow(),
                                 'QuickAPI error',
                                 str(e))
            return

        points = [QgsPointXY(location["lon"], location["lat"]) for location in locations]

        if len(points) < 2:
            raise InsufficientPoints("Please specify at least two points!")

        locations = [[point.x(), point.y()] for point in points]

        return locations

    @staticmethod
    def get_directions(provider: str, profile: str, method: str, locations: List[List[float]]) -> Direction:
        """Get the directions between locations from the specified provider with the specified method."""
        base_url = "http://localhost:8002" if provider == "Valhalla" else "http://localhost:5000"
        router = get_router_by_name(provider.lower())(base_url=base_url, client=QClient)

        direction_args = {"locations": locations, "profile": profile}
        if provider == "OSRM":
            direction_args.update({"overview": "full"})
        directions = router.directions(**direction_args)

        return directions

    def add_result_layer(self, provider: str, profile: str, directions: Direction) -> None:
        layer_out = QgsVectorLayer("LineString?crs=EPSG:4326",
                                   f"{provider} Route ({profile})",
                                   "memory")

        line = QgsLineString([QgsPoint(*coords) for coords in directions.geometry])
        feature = QgsFeature()
        feature.setGeometry(QgsGeometry(line))

        layer_out.dataProvider().addFeature(feature)
        layer_out.renderer().symbol().setWidth(1)
        layer_out.updateExtents()
        self.project.addMapLayer(layer_out)
        self._zoom_to_extent(layer_out, self.project)

    def _clear_annotations(self):
        for annotation in self.annotations:
            if annotation in self.project.annotationManager().annotations():
                self.project.annotationManager().removeAnnotation(annotation)
        self.annotations = []

    def closeEvent(self, event):
        for annotation in self.project.annotationManager().annotations():
            self.project.annotationManager().removeAnnotation(annotation)

    def on_provider_change(self, provider):
        self.selected_provider = provider
        self.waypoint_widget.update_waypoint_types(provider)

    def check_provider(self):
        self.waypoint_widget.update_waypoint_types(self.selected_provider)
