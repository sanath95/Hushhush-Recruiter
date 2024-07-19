from pandas import DataFrame, merge
from os.path import abspath, join, dirname, realpath
from json import load
from sklearn.preprocessing import normalize
from numpy import min, unique, mean, nan
import matplotlib.pyplot as plt
from scipy.spatial.distance import cdist
from sklearn.cluster import KMeans
from joblib import dump
from seaborn import pairplot
from sklearn.metrics import silhouette_samples

from sys import path
path.append(dirname(dirname(realpath(__file__))))
from Database import DBHandler

class Clustering:
    def __init__(self):    
        config_file = open(join(abspath(dirname(__file__)), 'machine_learning_config.json'))
        machine_learning_config = load(config_file)
        self.clustering_features = machine_learning_config["clustering_features"]

        self.cluster_column_name = machine_learning_config['cluster_column_name']

        self.db_handler = DBHandler()

    def _plot_elbow_graph(self, X, max_k=10):
        distortions = []
        inertias = []
        K = range(1, max_k)

        for k in K:
            kmeanModel = KMeans(n_clusters=k, random_state=42).fit(X)
            kmeanModel.fit(X)
        
            distortions.append(sum(min(cdist(X, kmeanModel.cluster_centers_, 'euclidean'), axis=1)) / X.shape[0])
            inertias.append(kmeanModel.inertia_)

        plt.plot(K, distortions, 'bx-')
        plt.xlabel('Values of K')
        plt.ylabel('Distortion')
        plt.title('The Elbow Method using Distortion')
        plt.savefig('./outputs/dist.png')
        plt.close()
        print('Saved elbow graph - distortion!')

        plt.plot(K, inertias, 'bx-')
        plt.xlabel('Values of K')
        plt.ylabel('Inertia')
        plt.title('The Elbow Method using Inertia')
        plt.savefig('./outputs/inertia.png')
        plt.close()
        print('Saved elbow graph - inertia!')

    def _create_clusters(self, k, X):
        kmeans = KMeans(n_clusters=k, init='k-means++', random_state=42)
        kmeans.fit(X)
        with open("./outputs/kmeans.pkl", "wb") as f:
            dump(kmeans, f)
        print('Saved kmeans model!')
        return kmeans.predict(X)
    
    def _pair_plot(self, df):
        pairplot(df, hue=self.cluster_column_name)
        plt.savefig('./outputs/pair_plot.png')
        plt.close()
        print('Saved pair plot!')

    def _silhouette_plot(self, X):
        for i, k in enumerate([2, 3, 4]):
            fig, (ax1, ax2) = plt.subplots(1, 2)
            fig.set_size_inches(18, 7)
            
            km = KMeans(n_clusters=k)
            labels = km.fit_predict(X)
            centroids = km.cluster_centers_

            silhouette_vals = silhouette_samples(X, labels)

            y_lower, y_upper = 0, 0
            for i, cluster in enumerate(unique(labels)):
                cluster_silhouette_vals = silhouette_vals[labels == cluster]
                cluster_silhouette_vals.sort()
                y_upper += len(cluster_silhouette_vals)
                ax1.barh(range(y_lower, y_upper), cluster_silhouette_vals, edgecolor='none', height=1)
                ax1.text(-0.03, (y_lower + y_upper) / 2, str(i + 1))
                y_lower += len(cluster_silhouette_vals)

            avg_score = mean(silhouette_vals)
            ax1.axvline(avg_score, linestyle='--', linewidth=2, color='green')
            ax1.set_yticks([])
            ax1.set_xlim([-0.1, 1])
            ax1.set_xlabel('Silhouette coefficient values')
            ax1.set_ylabel('Cluster labels')
            ax1.set_title('Silhouette plot for the various clusters', y=1.02)
            
            ax2.scatter(X[:, 0], X[:, 6], c=labels)
            ax2.scatter(centroids[:, 0], centroids[:, 6], marker='*', c='r', s=250)
            ax2.set_xlim([-2, 2])
            ax2.set_ylim([-2, 2])
            ax2.set_xlabel('Size')
            ax2.set_ylabel('Reputation')
            ax2.set_title('Visualization of clustered data', y=1.02)
            ax2.set_aspect('equal')
            plt.tight_layout()
            plt.suptitle(f'Silhouette analysis using k = {k}', fontsize=16, fontweight='semibold', y=1.05)

            plt.savefig(f'./outputs/silhouette_plot-{k}.png')
            plt.close()
            print(f'Saved silhouette plot {k}!')
    
    async def get_clusters(self):
        github_results = await self.db_handler.read_from_db('github')
        github_df = DataFrame([row[0] for row in github_results[0]], columns=github_results[1])
        stack_results = await self.db_handler.read_from_db('stackexchange')
        stack_df = DataFrame([row[0] for row in stack_results[0]], columns=stack_results[1])

        github_df.drop_duplicates(inplace=True, ignore_index=True)
        stack_df.drop_duplicates(inplace=True, ignore_index=True)
        
        github_df.sort_values(by=['followers'], inplace=True, ignore_index=True)
        github_df['merge_index'] = range(len(github_df))
        stack_df.sort_values(by=['reputation'], inplace=True, ignore_index=True)
        stack_df['merge_index'] = range(len(stack_df))

        combined_df = merge(github_df, stack_df, how='inner', on='merge_index')
        combined_df.drop(['merge_index'], axis=1, inplace=True)
        combined_df.replace('NaN', nan, inplace=True)
        combined_df.dropna(axis = 0, subset = self.clustering_features, inplace = True, ignore_index = True)

        X_array = combined_df[self.clustering_features].astype(float).to_numpy()
        X_norm = normalize(X_array, axis=1)

        self._plot_elbow_graph(X_norm)

        clusters = self._create_clusters(2, X_norm)

        df_norm = DataFrame(X_norm, columns = self.clustering_features)
        df_norm[self.cluster_column_name] = clusters
        combined_df[self.cluster_column_name] = clusters
        
        self._pair_plot(df_norm)

        self._silhouette_plot(X_norm)

        return combined_df