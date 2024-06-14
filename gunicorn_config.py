import os
import multiprocessing

bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"  # Default to port 8000 if $PORT is not set
workers = multiprocessing.cpu_count()  # Adjust the number of workers
threads = 1  # Start with a single thread
timeout = 200
loglevel = 'debug'

