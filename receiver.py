from utils.rabbit_mq_utils import RabbitMQConnection
from constants.constants import RabbitMQQueues
from virtual_piano.main import main


def receive(configuration):
    rabbit_mq_connection = RabbitMQConnection(configuration["rabbit-mq"]["host"])
    rabbit_mq_connection.declare_queue(queue=RabbitMQQueues.VIRTUAL_PIANO.value)

    def message_received_callback(ch, method, properties, message_body):
        print(f"A message has been received! Message: {message_body}")
        if message_body == b"start":
            main()

    rabbit_mq_connection.channel.basic_consume(
        queue=RabbitMQQueues.VIRTUAL_PIANO.value,
        on_message_callback=message_received_callback,
        auto_ack=True,
    )

    print("Waiting for messages...")
    rabbit_mq_connection.channel.start_consuming()
