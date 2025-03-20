from flask import Flask, request, jsonify
import os
import requests
import csv
from io import StringIO

app = Flask(__name__)


PV_DIR = "/Bindu_PV_dir "

os.makedirs(PERSISTENT_STORAGE, exist_ok=True)

@app.route('/store-file', methods=['POST'])
def store_file():
    data = request.json
    
    # Validate input
    if not data or 'file' not in data or not data['file']:
        return jsonify({"file": None, "error": "Invalid JSON input."}), 400
    
    if 'data' not in data:
        return jsonify({"file": data['file'], "error": "Invalid JSON input."}), 400
    
    try:
        # Ensure directory exists
        os.makedirs(PV_DIR, exist_ok=True)
        
        # Write data to file
        file_path = os.path.join(PV_DIR, data['file'])
        with open(file_path, 'w') as f:
            f.write(data['data'])
        
        return jsonify({"file": data['file'], "message": "Success."}), 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"file": data['file'], "error": "Error while storing the file to the storage."}), 500

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    
    # Validate input
    if not data or 'file' not in data or not data['file']:
        return jsonify({"file": None, "error": "Invalid JSON input."}), 400
    
    file_path = os.path.join(PV_DIR, data['file'])
    
    # Check if file exists
    if not os.path.exists(file_path):
        return jsonify({"file": data['file'], "error": "File not found."}), 404
    
    try:
        # Forward request to container 2
        response = requests.post(CONTAINER2_SERVICE, json=data)
        return response.json(), response.status_code
    except Exception as e:
        print(f"Error calling container 2: {str(e)}")
        return jsonify({"file": data['file'], "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
