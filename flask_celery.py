from flask import Flask
from celery import Celery

app = Flask(__name__)

# Celery configuration
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

# Create Celery instance
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# Define a simple task
@celery.task
def add(x, y):
    return x + y

# Example route using the Celery task
@app.route('/')
def index():
    result = add.delay(4, 4)
    return f'Task ID: {result.id}'

if __name__ == '__main__':
    app.run(debug=True)
