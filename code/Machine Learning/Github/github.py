from utils.api_calls import ApiCalls
from pandas import date_range, DataFrame
from datetime import datetime
from asyncio import gather, sleep
from time import time
from requests.utils import parse_header_links
from numpy import nan
from sklearn.preprocessing import LabelEncoder
from json import load
from os.path import abspath, join, dirname, realpath
from os import environ
from sys import path
path.append(dirname(dirname(realpath(__file__))))
from Database import DBHandler

class Github:
    def __init__(self):
        github_pat = environ.get('GITHUB_PAT')
        headers = {
                "Accept": "application/vnd.github+json", 
                "Authorization": f"Bearer {github_pat}", 
                "X-GitHub-Api-Version": "2022-11-28"
        }
        
        config_file = open(join(abspath(dirname(__file__)), 'github_config.json'))
        self.github_config = load(config_file)

        self.api_caller = ApiCalls(headers)
        self.db_handler = DBHandler()

    async def fetch_data(self):

        start_date = self.github_config['start_date']
        end_date = self.github_config['end_date']
        frequency = self.github_config['frequency']

        if (datetime.strptime(end_date, "%Y-%m-%d").date() > datetime.now().date()):
            end_date = datetime.now().date()

        dates = date_range(start = start_date, end = end_date, freq = frequency)
        dates = [date.strftime('%Y-%m-%d')+'T'+date.strftime('%H:%M:%S') for date in dates]

        urls = []
        for i in range(len(dates)):
            if i != len(dates)-1:
                urls.append(self.github_config['search_repos_between_dates_url'].format(dates[i], dates[i+1]))
            else:
                urls.append(self.github_config['search_repos_for_today_url'].format(dates[i]))

        batch_size = self.github_config['batch_size']
        split_urls = [urls[x:x+batch_size] for x in range(0,len(urls),batch_size)]

        for urls in split_urls:
            await gather(*[self.get_github_repos(url) for url in urls])

    async def get_github_repos(self, url):

        response_status_code, response_headers, response_body = None, None, None
        try:
            response_status_code, response_headers, response_body = await self.api_caller.async_http_get_call(url)
        except Exception as e:
            print(e)

        if response_status_code == 200:
            if 'items' in response_body.keys() and len(response_body['items']) > 0: 
                
                await self.data_preprocessing(DataFrame.from_records(response_body['items']))
                print(f'got {url}')

                # use response headers 'link' for pagination
                if 'link' in response_headers.keys():
                    links = response_headers['link']
                    links_parsed = parse_header_links(links.rstrip('>').replace('>,<', ',<'))
                    urls = [(lambda link: link['url'])(link) for link in links_parsed if link['rel'] == 'next']

                    if len(urls) != 0 and urls is not None:
                        await self.check_rate_limit(response_headers)
                        await self.get_github_repos(urls[0]) # recursive call to get next page data
        else:
            try:
                await self.check_rate_limit(response_headers)
            except Exception as e:
                print(e)
            print(response_body)
            await self.get_github_repos(url) # recursive call if secondary rate limit was hit

    async def data_preprocessing(self ,df):

        # drop columns
        df = df.drop([col for col in df.columns if 'url' in col], axis=1)

        cols_to_drop = self.github_config['columns_to_drop']
        df = df.drop(cols_to_drop, axis=1)

        # get name of owner
        def get_owner(row):
            if row['owner']['type'] == 'User':
                return row['owner']['login']
            else:
                return nan
        df['owner'] = df.apply(lambda row: get_owner(row), axis=1)
        df.dropna(inplace = True, ignore_index = True)

        # label encoding
        le_colls = self.github_config['columns_for_label_encoding']
        le = LabelEncoder()
        for col in le_colls:
            df[col] = le.fit_transform(df[col])

        # merge multiple repos of same user by taking mean of values
        avg_colls = self.github_config['columns_to_calculate_average']
        users = DataFrame(columns=df.columns)
        users['owner'] = df['owner'].unique()
        for col in avg_colls:
            for user in users['owner']:
                users.loc[users['owner'] == user, col] = df.loc[df['owner'] == user, col].mean()

        # get all languages and topics for user
        for user in users['owner']:
            this_user_langs = df.loc[df['owner'] == user, 'language']
            langs = []
            for lang in this_user_langs:
                langs.append(lang)
            users.loc[users['owner'] == user,'language'] = ', '.join(list(set(langs)))
            this_user_topics = df.loc[df['owner']==user, 'topics']
            topics = []
            for topic in this_user_topics:
                topics = topics + topic
            users.loc[users['owner'] == user,'topics'] = ', '.join(list(set(topics)))

        # get email and followers count of user
        user_urls = []
        for owner in users['owner']:
            user_urls.append(self.github_config['get_a_user_url'].format(owner))
        
        chunk_size = 10
        split_urls = [user_urls[x:x+chunk_size] for x in range(0,len(user_urls),chunk_size)]
        
        users_info = []
        for urls in split_urls:
            users_info = users_info + await gather(*[self.get_github_user(url) for url in urls])

        for info in users_info:
            if info is not None:
                users.loc[users['owner'] == info[0], 'email'] = info[1]
                users.loc[users['owner'] == info[0], 'followers'] = info[2]
                users.loc[users['owner'] == info[0], 'following'] = info[3]

        # save data
        await self.save_data(users)

    async def get_github_user(self, url):

        response_status_code, response_headers, response_body = None, None, None
        try:
            response_status_code, response_headers, response_body = await self.api_caller.async_http_get_call(url)
        except Exception as e:
            print(e)

        if response_status_code == 200:
            print(f'got {url.split('/')[-1]}')
            await self.check_rate_limit(response_headers)
            return response_body['login'], response_body['email'], response_body['followers'], response_body['following']
        else:
            try:
                await self.check_rate_limit(response_headers)
            except Exception as e:
                print(e)
            print(response_body)
            await self.get_github_user(url) # recursive call if secondary rate limit was hit

    async def check_rate_limit(self, response_headers):

        rate_limit_remaining = response_headers['x-ratelimit-remaining']
        rate_limit_reset = response_headers['x-ratelimit-reset']
        if int(rate_limit_remaining) == 0:
            print('Sleeping for ' + str(abs(float(rate_limit_reset) - time())))
            await sleep(abs(float(rate_limit_reset) - time()))

    async def save_data(self, df):

        place_holder_string = ('%s,' * len(df.columns)).rstrip(',')
        df_columns = df.columns.tolist()
        query = '''INSERT INTO github ({}) VALUES ({})'''.format(','.join(df_columns), place_holder_string)

        for i in range(len(df)):
            await self.db_handler.execute_query(query, df.iloc[i, :].tolist())