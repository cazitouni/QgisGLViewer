from qgis.core import QgsPointXY, QgsVectorLayer, QgsGeometry, QgsCoordinateTransform, QgsCoordinateReferenceSystem, QgsProject, Qgis
import sqlite3

def connector(x, y, params, date_selected=None):
    cursor = params['conn'].cursor()
    schema = params['schema']
    table = params['table']
    link = params['link']
    geom = params['geom']
    yaw = params['yaw']
    date = params['date']
    crs = params['crs']
    query_crs = 'SELECT ST_SRID({}) FROM "{}"."{}" LIMIT 1'.format(geom, schema, table)
    cursor.execute(query_crs)
    result_crs = cursor.fetchone()[0]
    query_dates = 'SELECT DISTINCT "{}" FROM "{}"."{}" WHERE ST_DWithin(ST_SetSRID("{}", {}), ST_SetSRID(ST_MakePoint({}, {}), {}), {}) ORDER BY "{}" DESC'.format(date, schema, table, geom, crs, x, y, crs, 5, date)
    try : 
        cursor.execute(query_dates)
        dates = cursor.fetchall()
        dates = [date[0] for date in dates]
    except Exception :
         dates = None
    if date_selected is None :
        date_selected = dates[0]
    query = 'SELECT "{}", "{}", ST_X("{}") as x, ST_Y("{}") as Y, "{}"  FROM "{}"."{}" WHERE ST_DWithin(ST_SetSRID("{}", {}), ST_SetSRID(ST_MakePoint({}, {}), {}), {}) AND "{}" = \'{}\' ORDER BY ST_Distance(ST_SetSRID("{}", {}), ST_SetSRID(ST_MakePoint({}, {}), {})) LIMIT 1'.format(link, yaw, geom, geom, date, schema, table, geom, crs, x, y, crs, 10, date, date_selected, geom, crs, x, y, crs)
    try : 
        cursor.execute(query)
        result = cursor.fetchone()
        url = result[0]
        direction = result[1]
        if result_crs == 4326:
            direction = 360 - (direction - 90)
        pointReal = QgsPointXY(result[2], result[3])
        year  = result[4]
    except Exception : 
        url = 0
        direction = None
        pointReal = None
        year = None
    
    return url, direction, pointReal, year, dates

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
    schema = params['schema']
    table = params['table']
    link = params['link']
    yaw = params['yaw']
    date = params['date']
    crs = params['crs']
    dates = []
    layer = QgsVectorLayer("{}|layername={}".format(schema, table), "images", "ogr")
    if layer.isValid():
        layer_crs = layer.crs().authid()
        crs = QgsCoordinateReferenceSystem(crs)
        transform = QgsCoordinateTransform(crs, QgsCoordinateReferenceSystem("EPSG:4326"), QgsProject.instance())
        point = QgsPointXY(x, y)
        point = transform.transform(point)
        point_geometry = QgsGeometry.fromPointXY(point)
        closest_features = []

        if date_selected is not None:
            for feature in layer.getFeatures():
                if feature[date] == date_selected:
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


        # Sort closest_features by geometry distance (closest first)
        closest_features.sort(key=lambda f: point_geometry.distance(f.geometry()))

        # Select the feature with the closest geometry
        closest_feature = closest_features[0]

        # Now, within the features with the same geometry, sort by date in descending order (most recent first)
        closest_features_same_geometry = [f for f in closest_features if f.geometry().equals(closest_feature.geometry())]
        closest_features_same_geometry.sort(key=lambda f: f[date], reverse=True)

        # Select the feature with the most recent date among those with the same geometry
        closest_feature = closest_features_same_geometry[0]


        url = closest_feature[link]
        direction = closest_feature[yaw]
        year = closest_feature[date]
        pointReal = QgsPointXY(closest_feature.geometry().asPoint())

        if layer_crs == "EPSG:4326":
            direction = 360 - (direction - 90)


        dates = sorted(set(dates), reverse=True)

        return url, direction, pointReal, year, dates
    else:
        return 0, None, None, None, None

