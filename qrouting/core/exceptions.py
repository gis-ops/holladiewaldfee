class QRoutingError(Exception):

    def __init__(self, message=None):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        if self.message is None:
            return ""
        else:
            return str(self.message)


class ProfileNotSupportedError(QRoutingError):
    """Is raised when a routing profile is chosen that is not available for the chosen routing service"""


class InsufficientPoints(QRoutingError):
    """Is raised when the points table has been populated with less than two points."""
