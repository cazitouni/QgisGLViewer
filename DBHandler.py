from qgis.core import QgsPointXY, QgsVectorLayer, QgsGeometry, QgsCoordinateTransform, QgsCoordinateReferenceSystem, QgsProject

def connector(x, y, params):
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
    print(result_crs)
    query = 'SELECT "{}", "{}", ST_X("{}") as x, ST_Y("{}") as Y, "{}"  FROM "{}"."{}" WHERE ST_DWithin(ST_SetSRID("{}", {}), ST_SetSRID(ST_MakePoint({}, {}), {}), {}) ORDER BY ST_Distance(ST_SetSRID("{}", {}), ST_SetSRID(ST_MakePoint({}, {}), {})) LIMIT 1'.format(link, yaw, geom, geom, date, schema, table, geom, crs, x, y, crs, 10, geom, crs, x, y, crs)
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

def connector_gpkg(x, y, params):
    schema = params['schema']
    table = params['table']
    link = params['link']
    yaw = params['yaw']
    date = params['date']
    crs = params['crs']
    layer = QgsVectorLayer("{}|layername={}".format(schema, table), "images", "ogr")
    if layer.isValid():
        layer_crs = layer.crs().authid()
        crs = QgsCoordinateReferenceSystem(crs)
        transform = QgsCoordinateTransform(crs, QgsCoordinateReferenceSystem("EPSG:4326"), QgsProject.instance())
        point = QgsPointXY(x, y)
        point = transform.transform(point)
        point_geometry = QgsGeometry.fromPointXY(point)
        closest_feature = min(layer.getFeatures(), key=lambda f: point_geometry.distance(f.geometry()))
        distance = point_geometry.distance(closest_feature.geometry())
        if distance > 10:
            return 0, None, None, None
        else:
            url = closest_feature[link]
            direction = closest_feature[yaw]
            year = closest_feature[date]
            pointReal = QgsPointXY(closest_feature.geometry().asPoint())  
        if layer_crs == "EPSG:4326" : 
            direction = 360 - (direction - 90)

        return url, direction, pointReal, year
