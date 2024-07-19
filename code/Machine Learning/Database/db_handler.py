from .db_connect import DBConnect
from json import load
from os.path import abspath, join, dirname
from pandas import read_csv

class DBHandler(DBConnect):

    def __init__(self):
        super().__init__()
        config_file = open(join(abspath(dirname(__file__)), 'db_config.json'))
        self.db_config = load(config_file)
        self._ensure_tables_exist()
        self._create_question_bank()

    def _ensure_tables_exist(self):
        conn = super().get_sync_connection()
        if conn is not None:
            with conn:
                with conn.cursor() as curr:
                    for table_name, table_columns in self.db_config['tables'].items():
                        collsstring = ', '.join([' '.join([x, y]) for x,y in table_columns.items()])
                        curr.execute('''CREATE TABLE IF NOT EXISTS public.{} (id SERIAL PRIMARY KEY, {})'''.format(table_name, collsstring))

    async def execute_query(self, query, values=None):
        conn = await super().get_connection()
        if conn is not None:
            async with conn:
                async with conn.cursor() as curr:
                    await curr.execute(query, values, prepare=True)

    async def read_from_db(self, table_name):
        colls = self.db_config['tables'][table_name].keys()
        query = '''SELECT ({columns}) FROM {table_name}'''.format(columns = ', '.join([col for col in colls]), table_name = table_name)
        conn = await super().get_connection()
        if conn is not None:
            async with conn:
                async with conn.cursor() as curr:
                    await curr.execute(query, prepare=True)
                    return await curr.fetchall(), colls
                
    def _create_question_bank(self):
        conn = super().get_sync_connection()
        if conn is not None:
            with conn:
                with conn.cursor() as curr:
                    df_path = join(abspath(dirname(__file__)), 'Ques_Bank.csv')
                    df = read_csv(df_path, index_col=False)
                    place_holder_string = ('%s,' * len(df.columns)).rstrip(',')
                    df_columns = df.columns.tolist()
                    query = '''INSERT INTO ques_bank ({}) VALUES ({})'''.format(','.join(df_columns), place_holder_string)
                    for i in range(len(df)):
                        curr.execute(query, df.iloc[i, :].tolist(), prepare=True)