import os
import pickle
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify

app = Flask(__name__)

# Define paths
base_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(base_dir, 'model.pkl')

# Load the model
if os.path.exists(model_path):
    print("Loading model from:", model_path)
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
else:
    model = None
    print("Warning: model.pkl not found! Please run model_building.py first.")

# Feature names in the exact training order
FEATURE_NAMES = [
    'IQ', 'Prev_Sem_Result', 'CGPA', 'Academic_Performance',
    'Extra_Curricular_Score', 'Communication_Skills',
    'Projects_Completed', 'Internship_Experience'
]

@app.route('/predict', methods=['POST'])
def predict():
    global model
    if model is None:
        # Try reloading the model if it was built after server startup
        if os.path.exists(model_path):
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
        else:
            return jsonify({'error': 'Model not loaded or model.pkl is missing. Run model_building.py first.'}), 500

    try:
        data = request.get_json(force=True)
    except Exception as e:
        return jsonify({'error': 'Invalid JSON or missing payload data'}), 400

    # We support either a single prediction dict or a list of prediction dicts
    if isinstance(data, dict):
        # Check if all required features are present
        missing_features = [f for f in FEATURE_NAMES if f not in data]
        if missing_features:
            return jsonify({'error': f'Missing features: {missing_features}'}), 400
        
        # Prepare input features
        input_data = pd.DataFrame([data])[FEATURE_NAMES]
    elif isinstance(data, list):
        # Bulk prediction input
        for item in data:
            if not isinstance(item, dict):
                return jsonify({'error': 'For batch prediction, payload must be a list of dictionaries.'}), 400
            missing_features = [f for f in FEATURE_NAMES if f not in item]
            if missing_features:
                return jsonify({'error': f'Missing features in batch item: {missing_features}'}), 400
        input_data = pd.DataFrame(data)[FEATURE_NAMES]
    else:
        return jsonify({'error': 'Payload must be a JSON object or list of objects.'}), 400

    try:
        # Perform prediction
        predictions = model.predict(input_data)
        probabilities = model.predict_proba(input_data)[:, 1] if hasattr(model, 'predict_proba') else None
        
        # Format response
        results = []
        for i, pred in enumerate(predictions):
            res = {
                'placement_prediction': int(pred),
                'status': 'Placed' if int(pred) == 1 else 'Not Placed'
            }
            if probabilities is not None:
                res['placement_probability'] = float(probabilities[i])
            results.append(res)
            
        return jsonify({
            'results': results[0] if isinstance(data, dict) else results
        })

    except Exception as e:
        return jsonify({'error': f'Prediction failed: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None
    })

if __name__ == '__main__':
    # Run application
    app.run(host='0.0.0.0', port=5000, debug=True)
