from qrouting.ui.config_dialogue_ui import Ui_settings_dialogue
from qgis.PyQt.QtWidgets import QDialog
from qgis.core import QgsMapLayerProxyModel, QgsProject
from qgis.PyQt.QtCore import pyqtSignal


class ConfigDialogue(QDialog, Ui_settings_dialogue):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.project = QgsProject.instance()
        self.setupUi(self)
        self.main_dialogue = self.parent().parent()
        self.avoid_layer_dropdown.setFilters(QgsMapLayerProxyModel.PointLayer)
        self.accepted.connect(self.save_settings)
        self.get_saved_settings_at_startup()

    def save_settings(self):
        self.save_avoid_layer_checked()
        self.project.writeEntry("qrouting", "avoid_layer_name", "test_layer")

    def save_avoid_layer_checked(self):
        if self.avoid_group.isChecked():
            a = self.avoid_layer_dropdown.currentLayer()
            self.main_dialogue.avoid_locations_layer = a
            self.project.writeEntryBool("qrouting", "avoid_layer_checked", True)
        else:
            self.project.writeEntryBool("qrouting", "avoid_layer_checked", False)

    def get_saved_settings_at_startup(self):
        avoid_layer_checked, _ = self.project.readBoolEntry("qrouting", "avoid_layer_checked", False)
        self.avoid_group.setChecked(avoid_layer_checked)
