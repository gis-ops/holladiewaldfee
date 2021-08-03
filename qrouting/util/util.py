from qgis.core import (
    QgsPointXY,
    QgsCoordinateReferenceSystem,
    QgsProject,
    QgsCoordinateTransform,
)


def to_wgs84(
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
