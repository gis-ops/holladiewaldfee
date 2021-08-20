from qrouting.ui.profile_widget_ui import Ui_ProfileWidget
from PyQt5.QtWidgets import QWidget, QToolButton
from PyQt5.QtCore import pyqtSignal
from .config_dialogue import ConfigDialogue
from ..core.routing import PROFILE_MAP


class ProfileWidget(Ui_ProfileWidget, QWidget):
    provider_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super(ProfileWidget, self).__init__(parent)
        self.setupUi(self)
        self.default_profile_button = self.profile_car
        self.previously_selected_button = self.default_profile_button
        self.profile_buttons.buttonReleased.connect(self.set_previously_selected)
        self.profile_button_list = [
            self.profile_bike,
            self.profile_mbike,
            self.profile_bus,
            self.profile_ped,
            self.profile_car,
        ]
        self.not_for_OSRM = [self.profile_mbike, self.profile_bus]
        self.active_button = self.get_active_button()
        for button in self.profile_button_list:
            name = PROFILE_MAP[button.objectName()]["repr"]
            button.setToolTip(name)

        self.config.clicked.connect(self.open_config_dialogue)

    def update_buttons(self, provider: str) -> None:
        if provider == "OSRM":
            for p_button in self.not_for_OSRM:
                name = PROFILE_MAP[p_button.objectName()]["repr"]
                if p_button.isChecked():
                    self.previously_selected_button = p_button
                    self.default_profile_button.setChecked(True)
                p_button.setEnabled(False)
                p_button.setToolTip(f"{name} (not available for OSRM)")
        else:
            for p_button in self.not_for_OSRM:
                name = PROFILE_MAP[p_button.objectName()]["repr"]
                p_button.setToolTip(name)
                p_button.setEnabled(True)

            if self.previously_selected_button in self.not_for_OSRM:
                self.previously_selected_button.setChecked(True)

    def open_config_dialogue(self):
        layer_dlg = ConfigDialogue(parent=self)
        layer_dlg.avoid_layer_selected.connect(self.set_avoid_layer)
        layer_dlg.exec_()

    def set_avoid_layer(self, layer):
        self.parent().avoid_locations_layer = layer

    def get_active_button(self) -> QToolButton:
        for p_button in self.profile_button_list:
            if p_button.isChecked():
                return p_button

    def set_previously_selected(self, button):
        self.previously_selected_button = button
