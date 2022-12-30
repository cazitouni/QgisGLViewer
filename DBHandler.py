from qgis.core import QgsPointXY, QgsVectorLayer, QgsGeometry, QgsCoordinateTransform, QgsCoordinateReferenceSystem, QgsProject

def connector(x, y, cursor, geom, schema, table, link, yaw, date, crs):
    query = 'SELECT {}, {}, ST_X({}) as x, ST_Y({}) as Y, {}  FROM "{}"."{}" WHERE ST_DWithin(ST_SetSRID({}, {}), ST_SetSRID(ST_MakePoint({}, {}), {}), {}) ORDER BY ST_Distance(ST_SetSRID({}, {}), ST_SetSRID(ST_MakePoint({}, {}), {})) LIMIT 1'.format(link, yaw, geom, geom, date, schema, table, geom, crs, x, y, crs, 10, geom, crs, x, y, crs)
    try : 
        cursor.execute(query)
        result = cursor.fetchone()
        url = result[0]
        direction = result[1]
        pointReal = QgsPointXY(result[2], result[3])
        year  = result[4]
    except Exception : 
        url = 0
        direction = None
        pointReal = None
        year = None
    cursor.close()
    return url, direction, pointReal, year

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

def connector_gpkg(x, y, link, yaw, date, crs, table, schema):
    layer = QgsVectorLayer("{}|layername={}".format(schema, table), "images", "ogr")
    if layer.isValid():
        crs = QgsCoordinateReferenceSystem(crs)
        transform = QgsCoordinateTransform(crs, QgsCoordinateReferenceSystem("EPSG:4326"), QgsProject.instance())
        point = QgsPointXY(x, y)
        point = transform.transform(point)
        point_geometry = QgsGeometry.fromPointXY(point)
        closest_feature = min(layer.getFeatures(), key=lambda f: point_geometry.distance(f.geometry()))
        url = closest_feature[link]
        direction = closest_feature[yaw]
        year = closest_feature[date]    
    return url, direction, point, year



