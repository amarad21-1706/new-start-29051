import multiprocessing

# Bind to the appropriate host and port
bind = "0.0.0.0:$PORT"

# Number of worker processes (default formula: cpu_count * 2 + 1)
workers = 2 # multiprocessing.cpu_count() * 2 + 1

# Number of threads per worker
threads = 2

# Timeout for requests (in seconds)
timeout = 120

# Log level
loglevel = 'debug'
