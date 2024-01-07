from flask import Flask, request, jsonify
import pandas as pd
from pymongo import MongoClient
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

#app = Flask(__name__)

# Function to extract data from a CSV file
def extract_data_from_csv(file_path):
    return pd.read_csv(file_path)

# Function to transform data
def transform_data(data):
    # Example transformation: converting column names to lowercase
    data.columns = map(str.lower, data.columns)
    return data

# Function to load data into MongoDB collection
def load_data_to_mongodb(data, mongodb_uri, db_name, collection_name):
    client = MongoClient(mongodb_uri)  # Connect to MongoDB
    db = client[db_name]  # Specify the database name
    collection = db[collection_name]  # Specify the collection name
    
    records = data.to_dict(orient='records')  # Convert DataFrame to a list of dictionaries
    collection.insert_many(records)  # Insert data into MongoDB collection

@app.route('/etl', methods=['POST'])
def etl_process():
    mongodb_uri = request.form.get('mongodb_uri')
    db_name = request.form.get('db_name')
    collection_name = request.form.get('collection_name')

    if not all([mongodb_uri, db_name, collection_name]):
        print(request.form)
        return jsonify({'error': 'Missing parameters'})
    
    uploaded_file = request.files['file']
    if uploaded_file.filename == '':
        return jsonify({'error': 'No file selected'})

    # Process the uploaded file (e.g., save it, perform ETL, etc.)
    # For example, saving the file locally
    print(uploaded_file)
    file_path = f"uploads/{uploaded_file.filename}"
    uploaded_file.save(file_path)

    try:
        data = extract_data_from_csv(file_path)
        transformed_data = transform_data(data)
        load_data_to_mongodb(transformed_data, mongodb_uri, db_name, collection_name)
        return jsonify({'message': 'ETL process completed successfully'})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == "__main__":
    app.run(debug=True)
