# run.py
import os
import sys
import logging

# Add the parent directory to the system path to ensure modules can be imported
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    logging.basicConfig(level=logging.DEBUG)
    logging.debug(f"Starting app on port {port}")
    app.run(debug=True, host='0.0.0.0', port=port)
