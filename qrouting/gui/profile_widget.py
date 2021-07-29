from qrouting.ui.profile_widget_ui import Ui_ProfileWidget
from PyQt5.QtWidgets import QWidget


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
