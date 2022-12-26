import math
from qgis.core import QgsPointXY

def connector(x, y, cursor, geom, schema, table, link, yaw):
    query = 'SELECT {}, {}, ST_X({}) as x, ST_Y({}) as Y  FROM "{}"."{}" WHERE ST_DWithin(ST_SetSRID({}, 3948), ST_SetSRID(ST_MakePoint({}, {}), 3948), {}) ORDER BY ST_Distance(ST_SetSRID({}, 3948), ST_SetSRID(ST_MakePoint({}, {}), 3948)) LIMIT 1'.format(link, yaw, geom, geom, schema, table, geom, x, y, 5, geom, x, y)
    cursor.execute(query)
    try : 
        result = cursor.fetchone()
        url = result[0]
        direction = result[1]
        pointReal = QgsPointXY(result[2], result[3])
    except Exception : 
        url = 0
        direction = None
        pointReal = None
    return url, direction, pointReal

def retrieve_columns(schema, table, cursor):
    query = "SELECT column_name FROM information_schema.columns WHERE table_name = %s AND table_schema = %s"
    cursor.execute(query, (table, schema))
    columns = [column[0] for column in cursor.fetchall()]
    cursor.close()
    return columns
