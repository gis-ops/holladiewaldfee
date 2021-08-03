from qrouting.ui.profile_widget_ui import Ui_ProfileWidget
from PyQt5.QtWidgets import QWidget

from ..core.routing import PROFILE_MAP


class ProfileWidget(Ui_ProfileWidget, QWidget):
    def __init__(self, parent=None):
        super(ProfileWidget, self).__init__(parent)
        self.setupUi(self)
        self.profile_buttons = [
            self.profile_bike,
            self.profile_mbike,
            self.profile_bus,
            self.profile_ped,
            self.profile_car,
        ]
        self.not_for_OSRM = [self.profile_mbike, self.profile_bus]
        for button in self.profile_buttons:
            name = PROFILE_MAP[button.objectName()]["repr"]
            button.setToolTip(name)

    def update_buttons(self, provider: str) -> None:
        is_not_osrm = True
        if provider == "OSRM":
            is_not_osrm = False

        for p_button in self.not_for_OSRM:
            p_button.setEnabled(is_not_osrm)
            name = PROFILE_MAP[p_button.objectName()]["repr"]
            if is_not_osrm:
                p_button.setToolTip(name)
            else:
                p_button.setToolTip(f"{name} (not available for OSRM)")
