from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from json import load
from os.path import abspath, join, dirname, realpath
from sklearn.preprocessing import normalize
from sklearn.metrics import confusion_matrix
from seaborn import heatmap
import matplotlib.pyplot as plt
from joblib import dump
from sys import path
path.append(dirname(dirname(realpath(__file__))))
from Database import DBHandler

class Classification:
    def __init__(self, df):
        self.db_handler = DBHandler()
        config_file = open(join(abspath(dirname(__file__)), 'machine_learning_config.json'))
        machine_learning_config = load(config_file)
        self.classification_features = machine_learning_config["classification_features"]
        self.cluster_column_name = machine_learning_config['cluster_column_name']
        self.test_size=machine_learning_config['test_size']

        y = df[self.cluster_column_name]
        X = df.drop([self.cluster_column_name], axis=1)
        self.X_train_df, self.X_test_df, self.y_train, self.y_test = train_test_split(X, y, test_size=self.test_size, random_state=42, stratify=y)

        self.X_train = normalize(self.X_train_df[self.classification_features].astype(float).to_numpy(), axis=1)
        self.X_test = normalize(self.X_test_df[self.classification_features].astype(float).to_numpy(), axis=1)

    def train_classifier(self):
        clf = LogisticRegression(random_state=42, solver='liblinear', penalty='l1').fit(self.X_train, self.y_train)
        print(f'Training score: {clf.score(self.X_train, self.y_train)}')
        print(f'Testing score: {clf.score(self.X_test, self.y_test)}')

        heatmap(confusion_matrix(self.y_test, clf.predict(self.X_test)), annot=True)
        plt.savefig('./outputs/confusion_matrix.png')
        plt.close()

        with open("./outputs/logit.pkl", "wb") as f:
            dump(clf, f)

        print('Classification done!')

    async def save_test_set(self):
        place_holder_string = ('%s,' * len(self.X_test_df.columns)).rstrip(',')
        df_columns = self.X_test_df.columns.tolist()
        query = '''INSERT INTO candidates ({}) VALUES ({})'''.format(','.join(df_columns), place_holder_string)

        for i in range(len(self.X_test_df)):
            await self.db_handler.execute_query(query, self.X_test_df.iloc[i, :].tolist())

        print('Test data stored to db!')