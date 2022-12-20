def connector(x, y, cursor):

    query = "SELECT lien_image FROM tmp.images WHERE ST_DWithin(ST_SetSRID(geom, 3948), ST_SetSRID(ST_MakePoint(%s, %s), 3948), %s) ORDER BY ST_Distance(ST_SetSRID(geom, 3948), ST_SetSRID(ST_MakePoint(%s, %s), 3948)) LIMIT 1"
    cursor.execute(query, (x, y, 5, x, y))
    try : 
        url = cursor.fetchone()[0]
    except Exception : 
        url = 0
    return url