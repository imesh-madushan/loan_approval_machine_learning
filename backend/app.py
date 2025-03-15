import pandas as pd
import pickle as pk
import numpy as np
import flask

# Model Predict loan approval
model_1 = pk.load(open('model_1.pkl','rb'))
# scaler_1 = pk.load(open('scaler_1.pkl','rb'))

# Model Loan Amount recommendation
model_2 = pk.load(open('model_2.pkl','rb'))

# Model Personalized Interest Rate (gives the cluster number)
model_3 = pk.load(open('model_3.pkl','rb'))
scaler_3 = pk.load(open('scaler_3.pkl','rb'))

# Model Fraud Detection
model_4 = pk.load(open('model_4.pkl','rb'))
scaler_4 = pk.load(open('scaler_4.pkl','rb'))

frud_threshold =  np.load('frud_threshold.npy')
cluster_means = pd.DataFrame(pd.read_csv('cluster_means.csv'))

app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route('/')
def welcome():
    return 'Welcome All'

@app.route('/check-approval',methods=["POST"])
def predict_loan_approval():
    col_oder = ['no_of_dependents','education','self_employed','income_annum','loan_amount','loan_term','cibil_score','assets']

    req = flask.request.get_json()
    new_data = pd.DataFrame(req,index=[0])

    # check if all the required columns are provided
    for col in col_oder:
        if col not in new_data.columns:
            return flask.jsonify({
                'error':'Please provide all the required columns',
                'required_columns':col_oder
            }),400
        
    new_data = new_data[col_oder] # reoder the columns as per the model trained

    prediction = model_1.predict(new_data)
    if prediction[0] == 1:
        #check if requested loan is a fraud
        if check_fraud(new_data) == True:
            return flask.jsonify({
                'approved': True,
                'fraud': True
            })
        else:
            return flask.jsonify({
                'approved': True,
                'fraud': False
            })
    else:
        return flask.jsonify({
            'approved': False
        })

@app.route('/recommend-loan',methods=["POST"])
def recommend_loan_amount():
    col_oder = ['income_annum', 'cibil_score', 'assets', 'loan_term', 'no_of_dependents', 'education', 'self_employed', 'loan_status']

    req = flask.request.get_json()
    new_data = pd.DataFrame(req,index=[0])
    
    # check if all the required columns are provided
    for col in col_oder:
        if col not in new_data.columns:
            return flask.jsonify({
                'error':'Please provide all the required columns',
                'required_columns':col_oder
            }),400
        
    new_data = new_data[col_oder] # reoder the columns as per the model trained
    prediction = model_2.predict(new_data).astype(int)

    #TODO: CHECK IF THE LOAN AMOUNT WILL BE FRAUD OR NOT

    return str(prediction[0])


@app.route('/interest-rate',methods=["POST"])
def cluster_number():
    col_oder = ["income_annum", "loan_amount"]

    req = flask.request.get_json()
    new_data = pd.DataFrame(req,index=[0])

    # check if all the required columns are provided
    for col in col_oder:
        if col not in new_data.columns:
            return flask.jsonify({
                'error':'Please provide all the required columns',
                'required_columns':col_oder
            }),400
    
    new_datax = new_data[col_oder]

    new_data_scaled = scaler_3.transform(new_datax)
    prediction = model_3.predict(new_data_scaled)

    mean_cibil_score = cluster_means['cibil_score'][prediction[0]]
    mean_assets = cluster_means['assets'][prediction[0]]

    #check if can be fraud or not using the mean values of other columns
    data_with_mean = pd.DataFrame({
        'income_annum': new_data['income_annum'],
        'loan_amount': new_data['loan_amount'],
        'cibil_score': mean_cibil_score,
        'assets': mean_assets
    })

    if check_fraud(data_with_mean) == True:
        base_rate = 10
        interest_rate = base_rate + cluster_means['Interest Rate'][prediction[0]]  

        return flask.jsonify({
            'interest_rate': interest_rate,
            'fraud': True
        })
    else:
        base_rate = 10
        interest_rate = base_rate + cluster_means['Interest Rate'][prediction[0]]        

        return flask.jsonify({
            'interest_rate': interest_rate,
            'fraud': False
        })


@app.route('/check-fraud',methods=["POST"])
def fraud_detection():
    req = flask.request.get_json()
    new_data = pd.DataFrame(req,index=[0])

    if check_fraud(new_data) == True:
        return flask.jsonify({
            'fraud': True
        })
    else:
        return flask.jsonify({
            'fraud': False
        })

# function to check if fraud or not
def check_fraud(data):
    col_oder = ["income_annum", "loan_amount", "cibil_score", "assets"]

    for col in col_oder:
        if col not in data.columns:
            return flask.jsonify({
                'error':'Please provide all the required columns',
                'required_columns':col_oder
            }),400

    new_data = data[col_oder]

    new_data_scaled = scaler_4.transform(new_data)
    prediction_clustor = model_4.predict(new_data_scaled)
    test_distance = np.linalg.norm(new_data_scaled - model_4.cluster_centers_[prediction_clustor])
    test_fraud = test_distance > frud_threshold
    return test_fraud

if __name__ == '__main__':
    app.run(port=5000)