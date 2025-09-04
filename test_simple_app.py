#!/usr/bin/env python3
"""
Simple test app to verify authentication endpoints
"""

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'Simple test app is running'
    })

@app.route('/api/auth/test', methods=['GET'])
def auth_test():
    return jsonify({
        'status': 'success',
        'message': 'Authentication endpoint is working'
    })

if __name__ == '__main__':
    print("Starting simple test app...")
    app.run(debug=True, host='0.0.0.0', port=5002)
