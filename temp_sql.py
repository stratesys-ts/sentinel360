import sqlite3
conn=sqlite3.connect('db.sqlite3')
cur=conn.cursor()
cur.execute("SELECT username,password FROM core_user WHERE username='admin'")
print(cur.fetchone())
