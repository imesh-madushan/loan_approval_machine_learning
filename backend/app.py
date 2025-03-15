import pandas as pd
import pickle as pk
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config["DEBUG"] = True

# load the models
model_1 = pk.load(open('model_1.pkl','rb'))
model_2 = pk.load(open('model_2.pkl','rb'))
model_3 = pk.load(open('model_3.pkl','rb'))
model_4 = pk.load(open('model_4.pkl','rb'))

# load the scalers
scaler_3 = pk.load(open('scaler_3.pkl','rb'))
scaler_4 = pk.load(open('scaler_4.pkl','rb'))

frud_threshold =  np.load('frud_threshold.npy')
cluster_means = pd.DataFrame(pd.read_csv('cluster_means.csv'))

@app.route('/check-approval',methods=["POST"])
def predict_loan_approval():
    col_oder = ['no_of_dependents','education','self_employed','income_annum','loan_amount','loan_term','cibil_score','assets']

    req = request.get_json()
    new_data = pd.DataFrame(req,index=[0])

    # check if all the required columns are provided
    for col in col_oder:
        if col not in new_data.columns:
            return jsonify({
                'error':'Please provide all the required columns',
                'required_columns':col_oder
            }),400
        
    new_data = new_data[col_oder] # reoder the columns as per the model trained

    prediction = model_1.predict(new_data)
    if prediction[0] == 1:
        #check if requested loan is a fraud
        if check_fraud(new_data) == True:
            return jsonify({
                'approved': True,
                'fraud': True
            })
        else:
            return jsonify({
                'approved': True,
                'fraud': False
            })
    else:
        return jsonify({
            'approved': False
        })

@app.route('/recommend-loan',methods=["POST"])
def recommend_loan_amount():
    col_oder = ['income_annum', 'cibil_score', 'assets', 'loan_term', 'no_of_dependents', 'education', 'self_employed']

    req = request.get_json()
    new_data = pd.DataFrame(req,index=[0])
    
    # check if all the required columns are provided
    for col in col_oder:
        if col not in new_data.columns:
            return jsonify({
                'error':'Please provide all the required columns',
                'required_columns':col_oder
            }),400
        
    new_data = new_data[col_oder] # reoder the columns as per the model trained

    #add 'loan_status' to the col_oder with default value 1, to always get approved loan amount
    new_data['loan_status'] = 1
    prediction = model_2.predict(new_data).astype(int)

    predicted_loan_amount = prediction[0]
    data_with_pred_data = pd.DataFrame({
        'income_annum': new_data['income_annum'],
        'loan_amount': predicted_loan_amount,
        'cibil_score': new_data['cibil_score'],
        'assets': new_data['assets'],
    })

    if check_fraud(data_with_pred_data) == True:
        #TODO: implement a better way to calculate the loan amount without fraud
        new_loan_no_fraud = best_loan_no_fraud(data_with_pred_data)

        if 'error' in new_loan_no_fraud:
            return jsonify({
                'error': str(new_loan_no_fraud['error'])
                })
        
        elif 'warning' in new_loan_no_fraud:
            return jsonify({
                'loan_amount': str(new_loan_no_fraud['loan_amount']),
                'warning': new_loan_no_fraud['warning']
            })
        else:
            return jsonify({
                'loan_amount': str(new_loan_no_fraud),
            })
    else:
        return jsonify({
            'loan_amount': str(predicted_loan_amount),
            'fraud': False
        })


@app.route('/interest-rate',methods=["POST"])
def cluster_number():
    col_oder = ["income_annum", "loan_amount"]

    req = request.get_json()
    new_data = pd.DataFrame(req,index=[0])

    # check if all the required columns are provided
    for col in col_oder:
        if col not in new_data.columns:
            return jsonify({
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

        return jsonify({
            'interest_rate': interest_rate,
            'fraud': True
        })
    else:
        base_rate = 10
        interest_rate = base_rate + cluster_means['Interest Rate'][prediction[0]]        

        return jsonify({
            'interest_rate': interest_rate,
            'fraud': False
        })


@app.route('/check-fraud',methods=["POST"])
def fraud_detection():
    req = request.get_json()
    new_data = pd.DataFrame(req,index=[0])

    if check_fraud(new_data) == True:
        return jsonify({
            'fraud': True
        })
    else:
        return jsonify({
            'fraud': False
        })

# function to check if fraud or not
def check_fraud(data):
    col_oder = ["income_annum", "loan_amount", "cibil_score", "assets"]

    for col in col_oder:
        if col not in data.columns:
            return jsonify({
                'error':'Please provide all the required columns',
                'required_columns':col_oder
            }),400

    new_data = data[col_oder]

    new_data_scaled = scaler_4.transform(new_data)
    prediction_clustor = model_4.predict(new_data_scaled)
    test_distance = np.linalg.norm(new_data_scaled - model_4.cluster_centers_[prediction_clustor])
    test_fraud = test_distance > frud_threshold
    return test_fraud

# when fruaud is detected, find the best possible loan amount
def best_loan_no_fraud(data):
    col_order = ["income_annum", "loan_amount", "cibil_score", "assets"]  # This contains the fraud loan amount
    reduce_limit_hit = False

    for col in col_order:
        if col not in data.columns:
            return jsonify({
                'error': 'Please provide all the required columns',
                'required_columns': col_order
            }), 400

    new_data = data[col_order]

    new_data_scaled = scaler_4.transform(new_data)
    prediction_cluster = model_4.predict(new_data_scaled)
    test_distance = np.linalg.norm(new_data_scaled - model_4.cluster_centers_[prediction_cluster])

    # if loan amount is causing fraud, reduce it step by step
    if test_distance > frud_threshold:
        step = 0.95  
        while test_distance > frud_threshold and new_data["loan_amount"].values[0] > 1000:  # Ensure loan amount doesn't go too low
            new_data["loan_amount"] *= step  # Reduce loan amount
            print(new_data["loan_amount"].values[0])
            new_data_scaled = scaler_4.transform(new_data)
            prediction_cluster = model_4.predict(new_data_scaled)
            test_distance = np.linalg.norm(new_data_scaled - model_4.cluster_centers_[prediction_cluster])

            #stop reducing if new loan amount is 70% of the original loan amount
            if new_data["loan_amount"].values[0] < 0.70 * data["loan_amount"].values[0]:
                reduce_limit_hit = True
                break

        if reduce_limit_hit:
            return {
                'error': 'Loan amount cannot be calculate without causing fraud'
            }
        else:
            return {
                'loan_amount': int(new_data["loan_amount"].values[0]),
                'warning': 'Actual predicted Loan amount reduced to avoid fraud'
            }

    return int(new_data["loan_amount"].values[0])


if __name__ == '__main__':
    app.run(port=5000)