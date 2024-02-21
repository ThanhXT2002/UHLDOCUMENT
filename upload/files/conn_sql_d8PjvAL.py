import pyodbc

conn_str = (
    "Driver={SQL Server};"
    "Server=LAPTOP-B8REBA8K\\SQLEXPRESS;"
    "Database=ql_user;"
    "Trusted_Connection=yes;"
)
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

for item in cursor.execute("select * from TTKH"):
    print(f"{item.id} {item.name} {item.email} {item.gender} {item.ip_address}")