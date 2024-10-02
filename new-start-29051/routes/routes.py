
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/increment', methods=['POST'])
def increment():
   # Process request and return response
   return jsonify({"message": "Incremented successfully"})

