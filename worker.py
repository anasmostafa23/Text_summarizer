import pika
import json
from app.utils import *
from app.database import *
from run import app
from sqlalchemy.exc import SQLAlchemyError
from config import Config 
import time


def wait_for_rabbitmq(connection_params, retries=10, delay=10):
    for i in range(retries):
        try:
            return pika.BlockingConnection(connection_params)
        except pika.exceptions.AMQPConnectionError as e:
            print(f"Attempt {i+1}/{retries} failed: Could not connect to RabbitMQ. Error: {e}")
            time.sleep(delay)
    raise Exception("Failed to connect to RabbitMQ after multiple attempts.")

# RabbitMQ connection parameters
connection_params = pika.ConnectionParameters(
    host='rabbitmq',  # Replace with your RabbitMQ server address
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


    def process_task_with_balance_deduction(user_id, prompt, result_summary):
        """Deduct balance in the worker after successfully processing the task."""
        user = User.query.filter_by(id=user_id).with_for_update().first()
        if user and user.balance >= 10:
            try:
                # Deduct balance only after processing
                user.balance -= 10
                transaction = Transaction(user_id=user.id, amount=-10, transaction_type='debit')
                db.session.add(transaction)

                task = MLTask(user_id=user.id, prompt=prompt, result=result_summary)
                db.session.add(task)

                db.session.commit()  # Commit all changes together
                return True
            except SQLAlchemyError as e:
                db.session.rollback()
                print(f"Error processing task or updating balance: {e}")
                return False
        else:
            print("Insufficient balance or user not found.")
            return False

    def callback(ch, method, properties, body):
        """Callback function with balance deduction logic."""
        try:
            task_data = json.loads(body)
            user_id = task_data.get('user_id')
            prompt = task_data.get('prompt')
            ngrok_url = Config.NGROK_URL
            print(f"{ngrok_url}")
            summary = summarize_text(prompt, ngrok_url)
            
            
            if summary :
        
                process_task_with_balance_deduction(user_id, prompt, summary)
                ch.basic_ack(delivery_tag=method.delivery_tag)

            else:
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                
        except Exception as e:
            print(f"Unexpected error: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)



    def worker_task():
        """Set up the worker to consume tasks from the queue."""
        connection = wait_for_rabbitmq(connection_params)  # Establish connection
        channel = connection.channel()
        
        # Declare the queue for the worker to listen to
        channel.queue_declare(queue='summarize_tasks', durable=True)

        # Start consuming messages
        channel.basic_consume(queue='summarize_tasks', on_message_callback=callback)
        print('Worker is waiting for messages...')
        channel.start_consuming()  # Continuously listen for new tasks

    if __name__ == "__main__":
        worker_task()  # Start the worker when the script is run
