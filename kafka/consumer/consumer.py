from kafka import KafkaConsumer
from json import loads
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Initialise kafka consumer
consumer = KafkaConsumer(
    'weblog',
    bootstrap_servers=['localhost:9099'],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='my-group',
    value_deserializer=lambda x: loads(x.decode('utf-8'))
)

engine = create_engine("postgresql://postgres:postgres@localhost:5432/kafka_log")
db = scoped_session(sessionmaker(bind=engine))

i = 0
# Read message from the kafka topic and push into the DB
for message in consumer:
    print("Message is:", message)
    message = message.value
    print("Message value is:", message)
    query = "INSERT INTO weblogdb (ip, time, url,status,method,http) VALUES ('{0}', '{1}', '{2}','{3}','{4}', '{5}');".format(
        message[0], message[1], message[2], message[3], message[4].replace("'", ""), message[5]
    )

    # push each row to DB
    db.execute(query)

    if i % 1000 == 0:
        print(message)
    i += 1

    db.commit()
    db.close()
