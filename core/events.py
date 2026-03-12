import os

producer = None

if os.getenv("ENABLE_KAFKA") == "true":
   from kafka import KafkaProducer
   producer = KafkaProducer(
       bootstrap_servers="localhost:9092"
   )