from psycopg import AsyncConnection, OperationalError, connect
from os import environ

class DBConnect:

    def __init__(self):
        self.host=environ.get('POSTGRES_HOST')
        self.port=environ.get('POSTGRES_PORT')
        self.dbname=environ.get('POSTGRES_DB')
        self.user=environ.get('POSTGRES_USER')
        self.password=environ.get('POSTGRES_PASSWORD')

    async def get_connection(self):
        try:
            conn = await AsyncConnection.connect(host=self.host, port=self.port, dbname=self.dbname, 
                                                                    user=self.user, password=self.password, 
                                                                    autocommit=True)
            return conn
        except OperationalError as e:
            print(e)
        except Exception as e:
            print(e)

    def get_sync_connection(self):
        try:
            conn = connect(host=self.host, port=self.port, dbname=self.dbname, user=self.user, password=self.password, autocommit=True)
            return conn
        except Exception as e:
            print(e)