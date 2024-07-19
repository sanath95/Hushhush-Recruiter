import requests
import pandas as pd
import time
from json import load
from os.path import abspath, join, dirname, realpath
from sys import path
path.append(dirname(dirname(realpath(__file__))))
from Database import DBHandler

class StackExchange:
    def __init__(self):
        config_file = open(join(abspath(dirname(__file__)), 'stackexchange_config.json'))
        self.stack_config = load(config_file)
        self.db_handler = DBHandler()

    def fetch_badges(self, start_user_id, end_user_id):
        api_url = self.stack_config["fetch_user_badges"]
        tb_gold = {}
        tb_silver = {}
        tb_bronze = {}
        tb_names = {}
        user_names = {}
        user_reputation = {}

        user_ids_range = list(range(start_user_id, end_user_id + 1))
        page = 1

        while True:
            response = requests.get(api_url.format(ids=";".join(map(str, user_ids_range)), page=page))
            if response.status_code == 200:
                data = response.json()
                print("Quota Remaining:", data['quota_remaining'])
                print("Quota Max:", data['quota_max'])

                for badge in data.get('items', []):
                    badge_name = badge['name']
                    if badge['badge_type'] == 'tag_based':
                        if badge['rank'] == 'gold':
                            user_id = badge['user']['user_id']
                            user_name = badge['user']['display_name']
                            user_names.setdefault(user_id,[]).append(user_name)
                            repu = badge['user']['reputation']
                            user_reputation.setdefault(user_id,[]).append(repu)
                            tb_gold.setdefault(user_id, []).append(badge_name)
                            tb_names.setdefault(user_id, []).append(badge_name)
                        elif badge['rank'] == 'silver':
                            user_id = badge['user']['user_id']
                            user_name = badge['user']['display_name']
                            user_names.setdefault(user_id,[]).append(user_name)
                            repu = badge['user']['reputation']
                            user_reputation.setdefault(user_id,[]).append(repu)
                            tb_silver.setdefault(user_id, []).append(badge_name)
                            tb_names.setdefault(user_id, []).append(badge_name)
                        elif badge['rank'] == 'bronze':
                            user_id = badge['user']['user_id']
                            user_name = badge['user']['display_name']
                            user_names.setdefault(user_id,[]).append(user_name)
                            repu = badge['user']['reputation']
                            user_reputation.setdefault(user_id,[]).append(repu)
                            tb_bronze.setdefault(user_id, []).append(badge_name)
                            tb_names.setdefault(user_id, []).append(badge_name)
                

                if not data.get('has_more', False) or data['quota_remaining'] < 10:
                    break  
                else:
                    page += 1  
            elif response.status_code == 502:
                    time.sleep(60)
                    self.fetch_badges(start_user_id, end_user_id)
            elif response.status_code == 503:
                    time.sleep(60)
                    self.fetch_badges(start_user_id, end_user_id)
            else:
                print(f"Error: {response.status_code} - {response.text}")
                break

            time.sleep(2) 

        return tb_gold,tb_silver,tb_bronze,tb_names,user_names,user_reputation

    async def write_to_postgresql(self, df):
        for _, row in df.iterrows():
            insert_query = """
                INSERT INTO stackexchange (
                    display_name, reputation, tb_gold, tb_silver, tb_bronze, 
                    tb_badge_names
                ) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            await self.db_handler.execute_query(insert_query, (
                row['Display Name'], row['Reputation'], row['T-B_Gold'], 
                row['T-B_Silver'], row['T-B_Bronze'], row['T-B_Badge_Names']
            ))

    async def fetch_data(self):
        start_user_id = self.stack_config["start_user_id"]
        end_user_id = self.stack_config["end_user_id"]
        batch_size = self.stack_config["batch_size"]

        for i in range(start_user_id, end_user_id, batch_size):
            tb_gold, tb_silver, tb_bronze, tb_names, user_names, user_reputation = self.fetch_badges(i, i + batch_size - 1)
            df = pd.DataFrame(columns=self.stack_config["feature_names"])

            for user_id in tb_names.keys():
                display_name = user_names.get(user_id, [""])[0]
                reputation = user_reputation.get(user_id,[""])[0]
                tb_gold_badge_ids = len(tb_gold.get(user_id, []))
                tb_silver_badge_ids = len(tb_silver.get(user_id, []))
                tb_bronze_badge_ids = len(tb_bronze.get(user_id, []))
                tb_badge_names = ",".join(tb_names.get(user_id, []))

                lst = [[user_id, display_name, reputation, tb_gold_badge_ids, tb_silver_badge_ids, tb_bronze_badge_ids, tb_badge_names]]
                df_extended = pd.DataFrame(lst, columns=self.stack_config["feature_names"])
                df = pd.concat([df, df_extended], ignore_index=True)
            
            df.drop(['Account ID'], axis=1)
            await self.write_to_postgresql(df)







