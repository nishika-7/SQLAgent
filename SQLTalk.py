import sqlite3

connection=sqlite3.connect("student.db")
cursor=connection.cursor()

table_info="""
create table STUDENT(
NAME VARCHAR(25),
CLASS VARCHAR(25),
SECTION VARCHAR(25),
MARKS INT
)
"""
cursor.execute(table_info)

cursor.execute('''Insert Into STUDENT values('Hope','Data Science','A',90)''')
cursor.execute('''Insert Into STUDENT values('NAM','Data Science','B',100)''')
cursor.execute('''Insert Into STUDENT values('JIM','Data Science','A',86)''')
cursor.execute('''Insert Into STUDENT values('NISH','Data Science','A',50)''')
cursor.execute('''Insert Into STUDENT values('TAE','DEVOPS','A',35)''')

print("The inserted rows are:")
data = cursor.execute("select * from STUDENT")
for row in data:
    print(row)

connection.commit()
connection.close()  