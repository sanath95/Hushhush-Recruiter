from psycopg import connect
from os import environ

def get_connection():
    host=environ.get('POSTGRES_HOST')
    port=environ.get('POSTGRES_PORT')
    dbname=environ.get('POSTGRES_DB')
    user=environ.get('POSTGRES_USER')
    password=environ.get('POSTGRES_PASSWORD')
    
    try:
        conn = connect(host=host, port=port, dbname=dbname, user=user, password=password, autocommit=True)
        return conn
    except Exception as e:
        print(e)
        return None

def get_test_data():
    conn = get_connection()
    if conn is not None:
        with conn:
            with conn.cursor() as curr:
                curr.execute('''SELECT * FROM candidates''', prepare=True)
                return curr.fetchall(), curr.description

def get_prospective_candidates(jobdesc):
    conn = get_connection()
    if conn is not None:
        with conn:
            with conn.cursor() as curr:
                curr.execute('''SELECT * FROM prospective WHERE selected_role = %s''', (jobdesc,), prepare=True)
                return curr.fetchall(), curr.description
            
def write_to_db(df):
    place_holder_string = ('%s,' * len(df.columns)).rstrip(',')
    df_columns = df.columns.tolist()
    query = '''INSERT INTO prospective ({}) VALUES ({})'''.format(','.join(df_columns), place_holder_string)
    conn = get_connection()
    if conn is not None:
        with conn:
            with conn.cursor() as curr:
                for i in range(len(df)):
                    curr.execute(query, df.iloc[i, :].tolist(), prepare=True)