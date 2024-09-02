import joblib
import pandas as pd
from datetime import datetime

def load_models():
    # Load pre-trained models and encoders
    model = joblib.load('models/model.pkl')
    scaler = joblib.load('models/scaler.pkl')
    onehot_encoder = joblib.load('models/onehot_encoder.pkl')
    return {'model': model, 'scaler': scaler, 'onehot_encoder': onehot_encoder}

def convert_to_unix_timestamp(date_str, time_str):
    dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
    return dt.timestamp()

def process_search(search_criteria, models):
    model = models['model']
    scaler = models['scaler']
    onehot_encoder = models['onehot_encoder']
    
    # Prepare search input
    search_timestamp = convert_to_unix_timestamp(search_criteria['date'], search_criteria['time'])
    search_destination_encoded = onehot_encoder.transform([[search_criteria['destination']]])
    
    search_input = pd.DataFrame(
        search_destination_encoded[0].tolist() + [search_timestamp, search_criteria['driver_rating']]
    ).T
    
    # Ensure column names match with scaler's expected features
    search_input.columns = scaler.feature_names_in_

    # Standardize the search input
    search_input_scaled = scaler.transform(search_input)
    
    # Find the nearest rides
    distances, indices = model.kneighbors(search_input_scaled)
    
    return distances, indices
