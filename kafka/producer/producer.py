from time import sleep
from json import dumps
from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
import json
import csv

admin_client = KafkaAdminClient(
    bootstrap_servers="localhost:9099",
    client_id='test'
)
# create kafka topic
topic_list = []
topic_list.append(NewTopic(name="weblog", num_partitions=1, replication_factor=1))
admin_client.create_topics(new_topics=topic_list, validate_only=False)

# Initialise a new kafka producer
producer = KafkaProducer(bootstrap_servers=['localhost:9099'],
                         value_serializer=lambda x:
                         json.dumps(x).encode('utf-8'))


with open('weblog_clean.csv') as file :
    reader = csv.reader(file, delimiter=",")

    i=0
    for row in reader:
        if i == 0:
            i += 1
            continue
        producer.send(topic='weblog', value=row)
        producer.flush()

