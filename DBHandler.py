from qgis.core import (
    QgsPointXY,
    QgsVectorLayer,
    QgsGeometry,
    QgsCoordinateTransform,
    QgsCoordinateReferenceSystem,
    QgsProject,
)
import psycopg2


def connector(x, y, params, date_selected=None):
    cursor = params["conn"].cursor()
    schema = params["schema"]
    table = params["table"]
    link = params["link"]
    geom = params["geom"]
    yaw = params["yaw"]
    date = params["date"]
    crs = params["crs"]
    query = (
        f"WITH pt AS (SELECT ST_SetSRID(ST_MakePoint({x}, {y}), {crs}) AS temp_geom)"
        f' SELECT DISTINCT ON ("{date}")'
        f' "{date}", "{link}", "{yaw}", ST_X("{geom}") AS x, ST_Y("{geom}") AS Y, ST_SRID({geom})'
        f' FROM "{schema}"."{table}", pt'
        f' WHERE ST_DWithin("{geom}", pt.temp_geom, 5)'
        f' ORDER BY "{date}" DESC, ST_Distance("{geom}", pt.temp_geom)'
    )
    try:
        cursor.execute(query)
    except psycopg2.Error as e:
        cursor.close()
        params["conn"].rollback()
        message = str(e)
        if "Operation on mixed SRID geometries" in message:
            message = " : Project CRS and layer CRS are differents"

        return 0, None, None, None, message
    data = cursor.fetchall()
    if data:
        dates = [str(date[0]) for date in data]
        if not date_selected or date_selected not in dates:
            date_selected = dates[0]
            url = data[dates.index(date_selected)][1]
            direction = float(data[dates.index(date_selected)][2])
            if data[dates.index(date_selected)][5] == 4326:
                direction = 360 - (direction - 90)
            pointReal = QgsPointXY(
                data[dates.index(date_selected)][3], data[dates.index(date_selected)][4]
            )
        else:
            url = data[dates.index(date_selected)][1]
            direction = float(data[dates.index(date_selected)][2])
            if data[dates.index(date_selected)][5] == 4326:
                direction = 360 - (direction - 90)
            pointReal = QgsPointXY(
                data[dates.index(date_selected)][3], data[dates.index(date_selected)][4]
            )
    else:
        url = 0
        direction = None
        pointReal = None
        dates = None
    return url, direction, pointReal, dates, None


def retrieve_columns(schema, table, cursor):
    query = "SELECT column_name FROM information_schema.columns WHERE table_name = %s AND table_schema = %s"
    cursor.execute(query, (table, schema))
    columns = [column[0] for column in cursor.fetchall()]
    cursor.close()
    return columns


def retrieve_columns_gpkg(cursor):
    cursor.execute("SELECT table_name FROM gpkg_contents")
    layer = cursor.fetchone()
    cursor.execute("PRAGMA table_info('{}')".format(layer[0]))
    results = cursor.fetchall()
    columns = []
    for result in results:
        columns.append(result[1])
    cursor.close()
    return columns, layer[0]


def connector_gpkg(x, y, params, date_selected=None):
    schema = params["schema"]
    table = params["table"]
    link = params["link"]
    yaw = params["yaw"]
    date = params["date"]
    crs = params["crs"]
    dates = []
    layer = QgsVectorLayer("{}|layername={}".format(schema, table), "images", "ogr")
    layer.loadNamedStyle("")
    if layer.isValid():
        layer_crs = layer.crs().authid()
        crs = QgsCoordinateReferenceSystem(crs)
        transform = QgsCoordinateTransform(
            crs, QgsCoordinateReferenceSystem("EPSG:4326"), QgsProject.instance()
        )
        point = QgsPointXY(x, y)
        point = transform.transform(point)
        point_geometry = QgsGeometry.fromPointXY(point)
        closest_features = []
        if date_selected is not None:
            for feature in layer.getFeatures():
                if feature[date].toString() == date_selected:
                    closest_features.append(feature)
                    dates.append(feature[date])
        else:
            for feature in layer.getFeatures():
                distance = point_geometry.distance(feature.geometry())
                if distance <= 10:
                    closest_features.append(feature)
                    dates.append(feature[date])
        if not closest_features:
            return 0, None, None, None, None
        closest_features.sort(key=lambda f: point_geometry.distance(f.geometry()))
        closest_feature = closest_features[0]
        closest_features_same_geometry = [
            f
            for f in closest_features
            if f.geometry().equals(closest_feature.geometry())
        ]
        closest_features_same_geometry.sort(key=lambda f: f[date], reverse=True)
        closest_feature = closest_features_same_geometry[0]
        url = closest_feature[link]
        direction = float(closest_feature[yaw])
        pointReal = QgsPointXY(closest_feature.geometry().asPoint())
        if layer_crs == "EPSG:4326":
            direction = 360 - (direction - 90)
        dates = sorted(set(dates), reverse=True)
        return url, direction, pointReal, dates, None
    else:
        return 0, None, None, None, None
