from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

PV_DIR = "/Bindu_PV_dir"
os.makedirs(PV_DIR, exist_ok=True)

CONTAINER2_SERVICE = os.getenv('PROCESSOR_SERVICE_URL')

def file_exists(filename):
    """Check if the given file exists in the mounted volume."""
    file_path = os.path.join(PV_DIR, filename)
    return os.path.exists(file_path)

def rename_to_csv_if_needed(filename):
    """If file is not a .csv, rename it to .csv"""
    file_path = os.path.join(PV_DIR, filename)
    
    if not os.path.exists(file_path):  # Ensure the file exists before renaming
        return filename, file_path

    if not filename.endswith(".csv"):
        new_filename = os.path.splitext(filename)[0] + ".csv"
        new_file_path = os.path.join(PV_DIR, new_filename)
        os.rename(file_path, new_file_path)
        return new_filename, new_file_path  # Return new name and path
    
    return filename, file_path

@app.route('/store-file', methods=['POST'])
def store_file():
    data = request.json
    
    # Validate input
    if not data or 'file' not in data or not data['file']:
        return jsonify({"file": None, "error": "Invalid JSON input."}), 400
    
    if 'data' not in data:
        return jsonify({"file": data['file'], "error": "Invalid JSON input."}), 400
    
    try:
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
    
    if 'product' not in data or not data['product']:
        return jsonify({"file": data['file'], "error": "Invalid JSON input."}), 400
    
    # Rename file to CSV if needed
    filename, file_path = rename_to_csv_if_needed(data['file'])
    
    # Check if file exists
    if not file_exists(filename):
        return jsonify({"file": data['file'], "error": "File not found."}), 404
    
    try:
        # Forward request to Container 2 with updated filename
        data['file'] = filename
        response = requests.post(CONTAINER2_SERVICE, json=data)
        
        # Ensure response is valid JSON
        response_data = response.json()
        response_data["file"] = data['file']  # Use original filename in response
        
        # Replace the filename in the response with the original filename
        response_data["file"] = data['file']
        
        return jsonify(response_data), response.status_code
    except Exception as e:
        print(f"Error calling container 2: {str(e)}")
        return jsonify({"file": data['file'], "error": "Error processing the request."}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)