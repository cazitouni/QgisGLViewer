from qgis.core import QgsPointXY
from datetime import datetime

def connector(x, y, cursor, geom, schema, table, link, yaw, date):
    query = 'SELECT {}, {}, ST_X({}) as x, ST_Y({}) as Y, {}  FROM "{}"."{}" WHERE ST_DWithin(ST_SetSRID({}, 3948), ST_SetSRID(ST_MakePoint({}, {}), 3948), {}) ORDER BY ST_Distance(ST_SetSRID({}, 3948), ST_SetSRID(ST_MakePoint({}, {}), 3948)) LIMIT 1'.format(link, yaw, geom, geom, date, schema, table, geom, x, y, 10, geom, x, y)
    cursor.execute(query)
    try : 
        result = cursor.fetchone()
        url = result[0]
        direction = result[1]
        pointReal = QgsPointXY(result[2], result[3])
        year  = result[4]
    except Exception : 
        url = 0
        direction = None
        pointReal = None
    return url, direction, pointReal, year

def retrieve_columns(schema, table, cursor):
    query = "SELECT column_name FROM information_schema.columns WHERE table_name = %s AND table_schema = %s"
    cursor.execute(query, (table, schema))
    columns = [column[0] for column in cursor.fetchall()]
    cursor.close()
    return columns
