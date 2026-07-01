from mysql.connector import connect as con


con = con(
    host="localhost",
    user="root",
    password = "root",
    database="fastapi_demo"
)

cur = con.cursor()


def get_data():
    query = "select * from contacts;"
    cur.execute(query)    
    r = cur.fetchall()
    return r
    





