from datetime import datetime

import psycopg2
import requests
from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsGeometry,
    QgsPointXY,
    QgsProject,
    QgsVectorLayer,
)


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
        f"WITH pt AS ("
        f"  SELECT ST_SetSRID(ST_MakePoint({x}, {y}), {crs}) AS temp_geom"
        f") "
        f'SELECT DISTINCT ON ("{date}") '
        f'  "{date}", "{link}", "{yaw}", '
        f'  ST_X("{geom}") AS x, ST_Y("{geom}") AS y, ST_SRID("{geom}") '
        f'FROM "{schema}"."{table}", pt '
        f'WHERE ST_DWithin("{geom}", pt.temp_geom, 5) '
        f'ORDER BY "{date}" DESC, ST_Distance("{geom}", pt.temp_geom)'
    )
    try:
        cursor.execute(query)
    except psycopg2.Error as e:
        cursor.close()
        params["conn"].rollback()
        message = str(e)
        if "Operation on mixed SRID geometries" in message:
            message = " : Project CRS and layer CRS are differents"
        return 0, None, None, None, message, None
    data = cursor.fetchall()
    if data:
        dates = [str(date[0]) for date in data]
        if not date_selected or date_selected not in dates:
            date_selected = dates[0]
        index = dates.index(date_selected)
        url = data[index][1]
        direction = float(data[index][2])
        if data[index][5] == 4326:
            direction = 360 - (direction - 90)
        pointReal = QgsPointXY(data[index][3], data[index][4])
    else:
        url = 0
        direction = None
        pointReal = None
        dates = None
        index = None

    return url, direction, pointReal, dates, None, index


def connector_gpkg(x, y, params, date_selected=None):
    schema = params["schema"]
    table = params["table"]
    link = params["link"]
    yaw = params["yaw"]
    date = params["date"]
    crs = params["crs"]
    layer_path = f"{schema}|layername={table}"
    layer = QgsVectorLayer(layer_path, "images", "ogr")
    if not layer.isValid():
        return 0, None, None, None, "Invalid GeoPackage layer", None
    input_crs = QgsCoordinateReferenceSystem(crs)
    layer_crs = layer.crs()
    if input_crs != layer_crs:
        transform = QgsCoordinateTransform(input_crs, layer_crs, QgsProject.instance())
        point = transform.transform(QgsPointXY(x, y))
    else:
        point = QgsPointXY(x, y)
    point_geometry = QgsGeometry.fromPointXY(point)
    nearest_features = {}
    for feature in layer.getFeatures():
        geom = feature.geometry()
        if geom and geom.distance(point_geometry) <= 5:
            feature_date = str(feature[date].toPyDate())
            if feature_date not in nearest_features:
                nearest_features[feature_date] = feature
            else:
                current_distance = geom.distance(point_geometry)
                existing_distance = (
                    nearest_features[feature_date].geometry().distance(point_geometry)
                )
                if current_distance < existing_distance:
                    nearest_features[feature_date] = feature
    if not nearest_features:
        return 0, None, None, None, "No features found within distance", None
    dates = sorted(nearest_features.keys(), reverse=True)
    if not date_selected or date_selected not in dates:
        date_selected = dates[0]
    selected_feature = nearest_features[date_selected]
    url = selected_feature[link]
    direction = float(selected_feature[yaw])
    if layer_crs.authid() == "EPSG:4326":
        direction = 360 - (direction - 90)
    point_real = selected_feature.geometry().asPoint()
    point_real_xy = QgsPointXY(point_real[0], point_real[1])

    return url, direction, point_real_xy, dates, None, dates.index(date_selected)


def connector_panoramax(x, y, params, date_selected=None):
    transform = QgsCoordinateTransform(
        QgsProject.instance().crs(),
        QgsCoordinateReferenceSystem("EPSG:4326"),
        QgsProject.instance(),
    )
    reverse_transform = QgsCoordinateTransform(
        QgsCoordinateReferenceSystem("EPSG:4326"),
        QgsProject.instance().crs(),
        QgsProject.instance(),
    )
    x, y = transform.transform(x, y).x(), transform.transform(x, y).y()
    url = (
        params["url"]
        + "/search?&place_distance=0-5&place_position="
        + str(x)
        + ","
        + str(y)
    )
    results = requests.get(url).json()
    if not results["features"]:
        return 0, None, None, None, None, None
    date_to_feature = {}
    for feature in results["features"]:
        datetime_str = feature["properties"].get("datetime")
        if datetime_str:
            feature_date = datetime.fromisoformat(datetime_str).date()
            if feature_date not in date_to_feature:
                date_to_feature[feature_date] = feature
    unique_dates = sorted(date_to_feature.keys(), reverse=True)
    selected_date_index = 0
    if date_selected:
        selected_date = datetime.strptime(date_selected, "%d-%m-%Y").date()
        if selected_date in date_to_feature:
            results["features"] = [date_to_feature[selected_date]]
        else:
            closest_date = min(unique_dates, key=lambda d: abs(d - selected_date))
            results["features"] = [date_to_feature[closest_date]]
        selected_date_index = (
            unique_dates.index(selected_date) if selected_date in unique_dates else 0
        )
    else:
        results["features"] = [date_to_feature[unique_dates[0]]]
    url = results["features"][0]["assets"]["hd"]["href"]
    direction = results["features"][0]["properties"]["view:azimuth"]
    pointReal = reverse_transform.transform(
        QgsPointXY(
            results["features"][0]["geometry"]["coordinates"][0],
            results["features"][0]["geometry"]["coordinates"][1],
        )
    )
    dates = [str(date.strftime("%d-%m-%Y")) for date in unique_dates]

    return url, direction, pointReal, dates, None, selected_date_index


def retrieve_columns(schema, table, cursor):
    query = (
        "SELECT column_name "
        "FROM information_schema.columns "
        "WHERE table_name = %s"
        "AND table_schema = %s"
    )
    cursor.execute(query, (table, schema))
    columns = [column[0] for column in cursor.fetchall()]
    cursor.close()
    return columns


def retrieve_columns_gpkg(cursor):
    cursor.execute("SELECT table_name FROM gpkg_contents")
    layer = cursor.fetchone()
    cursor.execute(f"PRAGMA table_info('{layer[0]}')")
    results = cursor.fetchall()
    columns = []
    for result in results:
        columns.append(result[1])
    cursor.close()
    return columns, layer[0]
