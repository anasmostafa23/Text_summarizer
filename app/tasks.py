import pika
import json

# Connection parameters for RabbitMQ
connection_params = pika.ConnectionParameters(
    host='localhost',  # RabbitMQ server address
    port=5672,         # Default RabbitMQ port
    virtual_host='/',  # Virtual host
    credentials=pika.PlainCredentials(
        username='user',  # Default username
        password='password'  # Default password
    ),
    heartbeat=30,
    blocked_connection_timeout=2
)

def publish_task_to_queue(task_data):
    """Publishes a task to RabbitMQ."""
    try:
        # Establish connection to RabbitMQ
        connection = pika.BlockingConnection(connection_params)
        channel = connection.channel()

        # Declare a queue (it should be durable)
        channel.queue_declare(queue='summarize_tasks', durable=True)

        # Convert the task data to a JSON string
        message = json.dumps(task_data)

        # Publish the message to the 'summarize_tasks' queue
        channel.basic_publish(
            exchange='',
            routing_key='summarize_tasks',
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2  # Ensure message is persistent
            )
        )
        print("Task sent to RabbitMQ.")

    except Exception as e:
        print(f"Failed to publish task: {e}")
    
    finally:
        # Always ensure the connection is closed
        connection.close()
