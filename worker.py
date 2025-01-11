import pika
import json
from app.utils import *
from app.database import *
from run import app
from flask import flash
# RabbitMQ connection parameters
connection_params = pika.ConnectionParameters(
    host='localhost',  # Replace with your RabbitMQ server address
    port=5672,          # Default RabbitMQ port
    virtual_host='/',   # Virtual host (usually '/')
    credentials=pika.PlainCredentials(
        username='user',  # Default username
        password='password'   # Default password
    ),
    heartbeat=30,
    blocked_connection_timeout=2
)
with app.app_context():

    def callback(ch, method, properties, body):
        """Callback function to handle tasks from the queue."""
        task_data = json.loads(body)
        user_id = task_data.get('user_id')
        prompt = task_data.get('prompt')
        ngrok_url = task_data.get('ngrok_url')
        print(f"**********************************{ngrok_url}***************************************************")
        summary = summarize_text(prompt, ngrok_url)
        
        # Store the result in the database
        user = User.query.filter_by(id=user_id).first()
        if user:
            task = MLTask(user_id=user_id, prompt=prompt, result=summary)
            db.session.add(task)
            db.session.commit()
        

        ch.basic_ack(delivery_tag=method.delivery_tag)  # Acknowledge the message

    def worker_task():
        """Set up the worker to consume tasks from the queue."""
        connection = pika.BlockingConnection(connection_params)  # Establish connection
        channel = connection.channel()
        
        # Declare the queue for the worker to listen to
        channel.queue_declare(queue='summarize_tasks', durable=True)

        # Start consuming messages
        channel.basic_consume(queue='summarize_tasks', on_message_callback=callback)
        print('Worker is waiting for messages...')
        channel.start_consuming()  # Continuously listen for new tasks

    if __name__ == "__main__":
        worker_task()  # Start the worker when the script is run
