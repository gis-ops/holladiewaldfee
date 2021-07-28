from typing import Union
from .exceptions import ProfileNotSupportedError

PROFILE_MAP = {
    "profile_ped": {"Valhalla": "pedestrian", "OSRM": "foot", "repr": "Pedestrian"},
    "profile_bike": {"Valhalla": "bicycle", "OSRM": "bike", "repr": "Bicycle"},
    "profile_mbike": {"Valhalla": "motorcycle", "repr": "Motorcycle"},
    "profile_bus": {"Valhalla": "bus", "repr": "Transit"},
    "profile_car": {"Valhalla": "auto", "OSRM": "car", "repr": "Car"}
}


def _get_profile_from_button_name(button_name: str, provider: str) -> Union[None, str]:
    try:
        return PROFILE_MAP[button_name][provider]
    except KeyError:
        raise ProfileNotSupportedError(f"{PROFILE_MAP[button_name]['repr']} mode is not supported by {provider}.")
