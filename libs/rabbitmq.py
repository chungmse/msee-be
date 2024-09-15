import pika

connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
recognize_channel = connection.channel()
recognize_channel.queue_declare(queue="recognize")
