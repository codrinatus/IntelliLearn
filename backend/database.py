import pyodbc

SERVER = 'tcp:intellilearndb.database.windows.net'
DATABASE = 'intellilearn'
USERNAME = 'intellilearn'
PASSWORD = 'Learningtime5'

conn_str = f'Driver={{ODBC Driver 18 for SQL Server}};Server={SERVER};Database={DATABASE};Uid={USERNAME};Pwd={PASSWORD}' \
           f';Encrypt=yes;TrustServerCertificate=no;Connection Timeout=60'


def connect():
    conn = pyodbc.connect(conn_str)
    return conn


def insert_questions(questions, table_name):
    # Connect to the database
    conn = connect()
    cursor = conn.cursor()

    for question in questions:
        query = f"""
        INSERT INTO {table_name} (question, choiceA, choiceB, choiceC, choiceD, correctchoiceletter, difficulty)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(
            query,
            question['question'],
            question['choiceA'],
            question['choiceB'],
            question['choiceC'],
            question['choiceD'],
            question['correctchoiceletter'],
            question['difficulty']
        )

    conn.commit()
    conn.close()
    print(f"Inserted {len(questions)} questions into {table_name}")
