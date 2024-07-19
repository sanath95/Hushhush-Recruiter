from flask import Flask
from joblib import load
from db_handler import get_test_data, get_prospective_candidates, write_to_db
from pandas import DataFrame, concat
from os.path import abspath, join, dirname
from sklearn.preprocessing import normalize
from json import load as jsonload

app = Flask(__name__)

@app.route("/candidates/<jobdesc>")
def candidate_selection(jobdesc):
    jobdesc = jobdesc.lower()

    prospective_candidates = get_prospective_candidates(jobdesc)

    if len(prospective_candidates[0]) == 0:
        config_file = open(join(abspath(dirname(__file__)), 'candidate_selection_config.json'))
        candidate_selection_config = jsonload(config_file)
        columns = [desc[0] for desc in prospective_candidates[1]]
        columns.remove('id')

        data = get_test_data()
        df = DataFrame(data[0], columns=[desc[0] for desc in data[1]])

        req_df = get_candidates_list_for_given_jobdesc(df, jobdesc)

        if (len(req_df) == 0):
            return "<p> No users found! </p>"

        clusters = get_clusters(req_df[candidate_selection_config['classification_features']])

        req_df['clusters'] = clusters

        selected_candidates = req_df[req_df['clusters']==0].copy()
        prospective_candidates_df = DataFrame(columns=columns)

        for i in range(len(selected_candidates)):
            row = selected_candidates.iloc[i, :]
            name = row['display_name']
            skills = ', '.join(list(set(row['language'].lower().split(",") + row['topics'].lower().split(",") + row['tb_badge_names'].lower().split(",")))).lstrip(',').rstrip(',')
            email = "sanath.vh@gmail.com"
            status = None
            q1 = None
            q2 = None
            q3 = None
            q4 = None
            selected_role = jobdesc
            prospective_candidates_df = concat([prospective_candidates_df, 
                                                DataFrame([[name, skills, email, status, q1, q2, q3, q4, selected_role]], 
                                                          columns=columns)], 
                                                ignore_index=True)
            
        write_to_db(prospective_candidates_df)
    
    prospective_candidates = get_prospective_candidates(jobdesc)
    prospective_candidates_df = DataFrame(prospective_candidates[0], columns=[desc[0] for desc in prospective_candidates[1]])

    return prospective_candidates_df.to_json(orient='records')

def get_model():
    with open("./outputs/logit.pkl", "rb") as f:
        model = load(f)
    return model

def get_candidates_list_for_given_jobdesc(df, jobdesc):
    req_df = DataFrame(columns=df.columns)

    for i in range(len(df)):
        if ((jobdesc in df.loc[i, 'language'].lower().split(",")) or (jobdesc in df.loc[i, 'topics'].lower().split(",")) or (jobdesc in df.loc[i, 'tb_badge_names'].lower().split(","))):
            req_df = concat([req_df, DataFrame([df.iloc[i, :]])], ignore_index=True)

    return req_df

def get_clusters(df):
    X_norm = normalize(df.astype(float).to_numpy(), axis=1)

    model = get_model()

    return model.predict(X_norm)