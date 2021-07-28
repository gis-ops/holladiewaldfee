from .layer_select_ui import Ui_Dialog
from qgis.PyQt.QtWidgets import QDialog
from qgis.PyQt.QtCore import pyqtSignal
from qgis.core import QgsMapLayerProxyModel


class LayerSelectDialog(QDialog, Ui_Dialog):

    layer_selected = pyqtSignal("QgsVectorLayer")

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.layer_choice.setFilters(QgsMapLayerProxyModel.PointLayer)
        self.buttonBox.accepted.connect(self.select_layer)

    def select_layer(self) -> None:
        self.layer_selected.emit(self.layer_choice.currentLayer())
        self.close()
