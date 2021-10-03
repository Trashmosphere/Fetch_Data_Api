import mariadb


def retrieve_tle_entries():
    try:
        conn = mariadb.connect(
            user="root",
            password="root",
            host="34.116.176.206",
            port=3306,
            database="spaceJunk"
        )
    except mariadb.Error as e:
        return "Error connecting to the database"

    cursor = conn.cursor()

    arr=[]

    cursor.execute("SELECT * FROM spaceObjectTle")
    for entry in cursor:
        arr.append(entry)

    conn.close()

    return {"data":arr}
