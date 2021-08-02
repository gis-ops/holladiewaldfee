from qrouting.ui.waypoint_widget_ui import Ui_WaypointWidget
from PyQt5.QtWidgets import QWidget, QAbstractScrollArea
from PyQt5.QtCore import pyqtSignal
from qgis.core import QgsPointXY, QgsVectorLayer, QgsCoordinateTransform
from qgis.gui import QgsTableWidgetItem
from qgis.PyQt.QtCore import QPersistentModelIndex
from qgis.core import Qgis
from qrouting.gui.cell_widget import WaypointTypeWidget
from qrouting.gui.layer_select_dialog import LayerSelectDialog
from typing import Union
from ..util.util import to_wgs84

from ..util.ui import VALHALLA_LOCATION_TYPES


class WayPointWidget(Ui_WaypointWidget, QWidget):
    point_added = pyqtSignal()
    layer_added = pyqtSignal()
    all_content_removed = pyqtSignal()

    def __init__(self, parent=None):
        super(WayPointWidget, self).__init__(parent)
        self.parent = parent
        self.setupUi(self)
        self.coord_table.setSizeAdjustPolicy(
            QAbstractScrollArea.AdjustToContents
        )
        self.item_count = 0
        self.layer_added.connect(lambda: self.add_wp.setDisabled(True))
        self.point_added.connect(lambda: self.add_from_layer.setDisabled(True))
        self.all_content_removed.connect(lambda: self.add_wp.setDisabled(False))
        self.all_content_removed.connect(lambda: self.add_from_layer.setDisabled(False))

    def add_to_table(self, point: QgsPointXY, waypoint_type: Union[None, str]=None) -> None:
        row_index = self.coord_table.rowCount()
        self.coord_table.insertRow(row_index)
        self.coord_table.setItem(row_index, 0, QgsTableWidgetItem(f"{point.y():.6f}"))
        self.coord_table.setItem(row_index, 1, QgsTableWidgetItem(f"{point.x():.6f}"))
        self.coord_table.setCellWidget(row_index, 2, WaypointTypeWidget())
        if waypoint_type:
            widget = self.coord_table.cellWidget(row_index, 2)
            type_index = widget.findText(waypoint_type)

            if type_index == -1:
                self.parent.iface.messageBar().pushMessage(
                    f"Faulty Waypoint Type", f"Type must be one of {VALHALLA_LOCATION_TYPES}, not {waypoint_type}",
                    level=Qgis.Warning, duration=3)
            widget.setCurrentIndex(type_index)
        self.coord_table.resizeColumnsToContents()
        self.point_added.emit()

    def move_item_down(self) -> None:  # https://stackoverflow.com/a/11930967/10955832
        row = self.coord_table.currentRow()
        column = self.coord_table.currentColumn()
        if row < self.coord_table.rowCount() - 1:
            self.coord_table.insertRow(row + 2)
            for i in range(self.coord_table.columnCount()):
                old_item = self.coord_table.takeItem(row, i)
                if old_item:
                    self.coord_table.setItem(row + 2, i, old_item)
                else:
                    waypoint_cell_widget_index = self.coord_table.cellWidget(row, i).currentIndex()
                    self.coord_table.setCellWidget(row + 2, i, WaypointTypeWidget())
                    self.coord_table.cellWidget(row + 2, i).setCurrentIndex(waypoint_cell_widget_index)
                self.coord_table.setCurrentCell(row + 2, column)

            self.coord_table.removeRow(row)

    def move_item_up(self) -> None:
        row = self.coord_table.currentRow()
        column = self.coord_table.currentColumn()
        if row > 0:
            self.coord_table.insertRow(row - 1)
            for i in range(self.coord_table.columnCount()):
                old_item = self.coord_table.takeItem(row + 1, i)
                if old_item:
                    self.coord_table.setItem(row - 1, i, old_item)
                else:
                    waypoint_cell_widget_index = self.coord_table.cellWidget(row + 1, i).currentIndex()
                    self.coord_table.setCellWidget(row - 1, i, WaypointTypeWidget())
                    self.coord_table.cellWidget(row - 1, i).setCurrentIndex(waypoint_cell_widget_index)
                self.coord_table.setCurrentCell(row - 1, column)
            self.coord_table.removeRow(row + 1)

    def clear_table(self) -> None:
        row_indices = set(QPersistentModelIndex(index) for index in self.coord_table.selectedIndexes())
        if row_indices:
            for row_index in row_indices:
                self.coord_table.removeRow(row_index.row())
                self.item_count -= 1
        else:
            self.coord_table.setRowCount(0)
            self.all_content_removed.emit()
            self.item_count = 0

    def open_layer_selection(self) -> None:
        layer_dlg = LayerSelectDialog(parent=self)
        layer_dlg.layer_and_field_selected.connect(self._handle_layer)
        layer_dlg.exec_()

    def _handle_layer(self, list) -> None:

        layer = list[0]
        field = list[1]
        for idx, feature in enumerate(layer.getFeatures()):
            point = to_wgs84(
                point=feature.geometry().asPoint(),
                own_crs=layer.crs(),
                direction=QgsCoordinateTransform.ForwardTransform
            )
            try:
                type_ = feature.attribute(field)
            except KeyError:
                type_ = None
            self.add_to_table(point, type_)
            self.item_count += 1
        self.layer_added.emit()

    def update_waypoint_types(self, provider: str) -> None:
        if provider == "Valhalla":
            self.set_all_cell_widgets(True, "For more information on waypoint types, please check the Valhalla documentation.")
        elif provider == "OSRM":
            self.set_all_cell_widgets(False, "Waypoints are not supported for OSRM")

    def set_all_cell_widgets(self, boolean: bool, tooltip: str) -> None:
        for i in range(self.coord_table.rowCount()):
            self.coord_table.cellWidget(i, 2).setEnabled(boolean)
            self.coord_table.cellWidget(i, 2).setToolTip(tooltip)

    def get_all_rows(self):
        """Generator method for row-wise access of table items."""
        for idx, row in enumerate(range(self.coord_table.rowCount())):
            lat, lon = (
                float(self.coord_table.item(row, 0).text()),
                float(self.coord_table.item(row, 1).text()),
            )
            widget = self.coord_table.cellWidget(row, 2)
            yield idx, lat, lon, widget
