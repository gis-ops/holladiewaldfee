from qgis.core import QgsPointXY, QgsCoordinateReferenceSystem, QgsProject, QgsCoordinateTransform


def _trans(value, index):
    """
    Copyright (c) 2014 Bruno M. Custódio
    Copyright (c) 2016 Frederick Jansen
    https://github.com/hicsail/polyline/commit/ddd12e85c53d394404952754e39c91f63a808656
    """
    byte, result, shift = None, 0, 0

    while byte is None or byte >= 0x20:
        byte = ord(value[index]) - 63
        index += 1
        result |= (byte & 0x1F) << shift
        shift += 5
        comp = result & 1

    return ~(result >> 1) if comp else (result >> 1), index


def _decode(expression, precision=5, is3d=False):
    """
    Copyright (c) 2014 Bruno M. Custódio
    Copyright (c) 2016 Frederick Jansen
    https://github.com/hicsail/polyline/commit/ddd12e85c53d394404952754e39c91f63a808656
    """
    coordinates, index, lat, lng, z, length, factor = (
        [],
        0,
        0,
        0,
        0,
        len(expression),
        float(10 ** precision),
    )

    while index < length:
        lat_change, index = _trans(expression, index)
        lng_change, index = _trans(expression, index)
        lat += lat_change
        lng += lng_change
        if not is3d:
            coordinates.append((lat / factor, lng / factor))
        else:
            z_change, index = _trans(expression, index)
            z += z_change
            coordinates.append((lat / factor, lng / factor, z / 100))

    return coordinates


def decode_polyline5(polyline, is3d=False):
    """Decodes an encoded polyline string which was encoded with a precision of 5.
    :param polyline: An encoded polyline, only the geometry.
    :type polyline: str
    :param is3d: Specifies if geometry contains Z component. Currently only GraphHopper and OpenRouteService
        support this. Default False.
    :type is3d: bool
    :returns: List of decoded coordinates with precision 5.
    :rtype: list
    """

    return _decode(polyline, precision=5, is3d=is3d)


def decode_polyline6(polyline, is3d=False):
    """Decodes an encoded polyline string which was encoded with a precision of 6.
    :param polyline: An encoded polyline, only the geometry.
    :type polyline: str
    :param is3d: Specifies if geometry contains Z component. Currently only GraphHopper and OpenRouteService
        support this. Default False.
    :type is3d: bool
    :returns: List of decoded coordinates with precision 6.
    :rtype: list
    """

    return _decode(polyline, precision=6, is3d=is3d)

def maybe_transform_wgs84(
    point: QgsPointXY, own_crs: QgsCoordinateReferenceSystem, direction: int
) -> QgsPointXY:
    """
    Transforms the ``point`` to (``direction=ForwardTransform``) or from
    (``direction=ReverseTransform``) WGS84.
    """
    wgs84 = QgsCoordinateReferenceSystem.fromEpsgId(4326)
    project = QgsProject.instance()
    out_point = point
    if own_crs != wgs84:
        xform = QgsCoordinateTransform(own_crs, wgs84, project)
        point_transform = xform.transform(point, direction)
        out_point = point_transform

    return out_point
