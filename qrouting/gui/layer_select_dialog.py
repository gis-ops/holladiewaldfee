from qrouting.ui.layer_select_ui import Ui_Dialog
from qgis.PyQt.QtWidgets import QDialog
from qgis.PyQt.QtCore import pyqtSignal
from qgis.core import QgsMapLayerProxyModel, QgsFieldProxyModel, QgsVectorLayer


class LayerSelectDialog(QDialog, Ui_Dialog):

    layer_and_field_selected = pyqtSignal(list)
    # field_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.layer_choice.setFilters(QgsMapLayerProxyModel.PointLayer)
        # self.field_choice.setFilters(QgsFieldProxyModel.String)
        self.buttonBox.accepted.connect(self.select_layer)
        self.selected_layer = self.layer_choice.currentLayer()
        self.layer_choice.layerChanged.connect(self.update_field_choice_box)
        self.field_choice.setLayer(self.selected_layer)

    def select_layer(self) -> None:
        self.layer_and_field_selected.emit([self.layer_choice.currentLayer(), self.field_choice.currentField()])
        # self.field_selected.emit(self.field_choice.currentField())
        self.close()

    def update_field_choice_box(self, idx):
        self.selected_layer = self.layer_choice.currentLayer()
        self.field_choice.setLayer(self.selected_layer)


