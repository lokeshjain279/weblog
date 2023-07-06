# weblog
Web Log analysis using Kafka


### The project has following main components.
•	Kafka server

•	Zookeeper server

•	Postgres db

•	Kafka Consumer

•	Flask app

### This is how the workflow is :-
•	Kafka server and zookeeper is started.

•	Postgres db is setup and log database is created.

•	Some data pre-processing is done on the weblog.csv file. I am splitting the URL column into URL, status, method, http like this. data_format.ipynb file does this.


•	Creating a kafka topic using kafkaadminclient programmatically.

•	Producer is reading one row of csv file at a time and sending to the  kafka topic

•	Consumer is reading the message and pushing each row to the created table in postgres db using sqlalchemy.

•	Flask API is connected to database and following GET API’s are exposed :-

    - /weblog  - This returns following result as asked –

     - 5 most requested URLS

     - Hour wise frequency of logs
     
     - Peak Time of POST and GET
     
     - /ratio?url=/login.php – This returns Ratio of status code 200 vs other status code for a given URL. url is taken as a query parameter
     
     - /logcount?time="2017-11-29 6:58:55" – This returns Number of logs at a given time.

### Steps to run the project.

•	Postgres DB -

```
docker run --name kafka-postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres
```

•	This will start the postgres container.  Connect to the db with psql cli and create database.

```
psql -h localhost -p 5432 -d postgres -U postgres –password
CREATE DATABASE kafka_log;
```



•	Zookeeper server - Start the containerised zookeeper server.  I have used bitnami docker image that’s available.

```
docker network create kafka-net --driver bridge
docker run --name zookeeper-server -p 2181:2181 --network kafka-net -e ALLOW_ANONYMOUS_LOGIN=yes bitnami/zookeeper:latest
```


•	Kafka Server - Start the containerised kafka server.

```
docker run --name kafka-server --network kafka-net -e ALLOW_PLAINTEXT_LISTENER=yes -e KAFKA_CFG_ZOOKEEPER_CONNECT=zookeeper-server:2181 -e KAFKA_CFG_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092 -p 9092:9092 bitnami/kafka:latest
```

•	Move to weblog/kafka/producer folder
•	Kafka Producer - Build producer docker image and run the producer container :-

```
docker build -t kafka_producer -f Dockerfile_producer.yaml .
docker run –name kafka_producer kafka_producer
```



•	Kafka Consumer - Move to weblog/kafka/consumer folder
•	Build consumer docker image and run the container image :-

```
docker build -t kafka_consumer -f Dockerfile_consumer.yaml .
docker run –name kafka_consumer kafka_consumer
```

•	Flask API - Go to weblog/api folder.
•	Run these commands to initialise the database .

```
$ flask db init
$ flask db migrate
$ flask db upgrade
```


•	Build flask api Docker image:-

```
docker build --tag kafka_flask .
docker run --name kafka_flask -p 5000:5000 kafka_flask
```


•	Open the flask app at localhost:5000/weblog. Following API end points have been exposed:-
    
    - /weblog

    - ratio?url=/login.php
    
    - /logcount?time="2017-11-29 6:58:55"



###Things to improve :-

•	Add docker-compose script to build and run all the component once.