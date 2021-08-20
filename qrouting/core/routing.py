from typing import Union, List
from qgis.core import QgsVectorLayer, QgsCoordinateTransform, QgsPointXY
from .exceptions import ProfileNotSupportedError
from ..util.util import to_wgs84

PROFILE_MAP = {
    "profile_ped": {
        "Valhalla": "pedestrian",
        "OSRM": "foot",
        "repr": "Pedestrian",
    },
    "profile_bike": {"Valhalla": "bicycle", "OSRM": "bike", "repr": "Bicycle"},
    "profile_mbike": {"Valhalla": "motorcycle", "repr": "Motorcycle"},
    "profile_bus": {"Valhalla": "bus", "repr": "Transit"},
    "profile_car": {"Valhalla": "auto", "OSRM": "car", "repr": "Car"},
}


def _get_profile_from_button_name(
    button_name: str, provider: str
) -> Union[None, str]:
    try:
        return PROFILE_MAP[button_name][provider]
    except KeyError:
        raise ProfileNotSupportedError(
            f"{PROFILE_MAP[button_name]['repr']} mode is not supported by {provider}."
        )


def build_locations_from_layer(layer: QgsVectorLayer) -> List[List[float]]:
    locations = []
    for idx, feature in enumerate(layer.getFeatures()):
        point: QgsPointXY = to_wgs84(
            point=feature.geometry().asPoint(),
            own_crs=layer.crs(),
            direction=QgsCoordinateTransform.ForwardTransform,
        )
        locations.append([point.x(), point.y()])
    return locations
