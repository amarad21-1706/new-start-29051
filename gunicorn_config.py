import os
import multiprocessing

bind = f"0.0.0.0:{os.environ.get('PORT', '10000')}"  # Default to port 8000 if $PORT is not set
workers = 1
threads = 1  # Start with a single thread
timeout = 200
loglevel = 'debug'

