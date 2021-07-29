from qgis.PyQt.QtWidgets import QComboBox
from ..util.ui import VALHALLA_LOCATION_TYPES


class WaypointTypeWidget(QComboBox):
    def __init__(self, parent=None):
        super(WaypointTypeWidget, self).__init__(parent)
        self.addItems(VALHALLA_LOCATION_TYPES)
        # self.currentIndexChanged.connect(self.get_location_type)



