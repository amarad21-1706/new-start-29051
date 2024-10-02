
import multiprocessing

bind = "0.0.0.0:$PORT"
workers = 1 # multiprocessing.cpu_count() * 2 + 1
threads = 2
timeout = 120
loglevel = 'debug'
