from clustering import Clustering
from asyncio import run, gather
from Stackexchange import StackExchange
from Github import Github
from classification import Classification
from os.path import exists
from os import mkdir

async def select_candidates():
    stackexchange = StackExchange()
    github = Github()
    await gather(stackexchange.fetch_data(), github.fetch_data())

    if not exists('./outputs'):
        mkdir('./outputs')

    clustering = Clustering()
    df = await clustering.get_clusters()

    classification = Classification(df)
    await classification.save_test_set()
    classification.train_classifier()

if __name__ == '__main__':
    run(select_candidates())