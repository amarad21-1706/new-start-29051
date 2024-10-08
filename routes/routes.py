
from flask import Flask, jsonify
from forms.forms import MainForm

app = Flask(__name__)

@app.route('/api/increment', methods=['POST'])
def increment():
   # Process request and return response
   return jsonify({"message": "Incremented successfully"})

