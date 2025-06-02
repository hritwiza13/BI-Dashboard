from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
import os
from datetime import datetime
from data_handler import fetch_sales_data

app = Flask(__name__, static_folder='frontend')
CORS(app)  # Enable CORS for all routes

# Get port from environment variable or use default
port = int(os.environ.get('PORT', 5000))

@app.route('/')
def index():
    return send_from_directory('frontend', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('frontend', path)

@app.route('/api/data', methods=['GET'])
def get_data():
    try:
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')

        if not start_date_str or not end_date_str:
            return jsonify({'error': 'Missing start_date or end_date parameters'}), 400

        try:
            start_date = datetime.fromisoformat(start_date_str)
            end_date = datetime.fromisoformat(end_date_str)
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

        df = fetch_sales_data(start_date, end_date)
        
        if df.empty:
            return jsonify([])

        # Convert dataframe to a list of dictionaries for JSON response
        data = df.to_dict(orient='records')
        return jsonify(data)

    except Exception as e:
        print(f"Error in get_data: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port) 