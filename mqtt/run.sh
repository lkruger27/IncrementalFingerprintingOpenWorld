#!/bin/sh
# sudo apt-get install mosquitto

# kill all running java clients
sudo pkill -9 -f assignment2

# to make sure everything is installed from scratch
sudo docker stop $(sudo docker ps -a -q)
sudo docker rm -vf $(sudo docker ps -a -q)
# sudo docker rmi -f $(sudo docker images -aq) # to also remove images

sudo docker run --name hivemq-ce -d -p 1884:1883 hivemq/hivemq-ce
# sudo docker restart hivemq-ce
sleep 1
java -jar mqtt.jar 1884 &
sleep 1
python3 main.py hivemq-ce --new_file
sudo docker stop hivemq-ce
# kill background process
sudo pkill -9 -f mqtt.jar

sudo docker run -d --name emqx -p 1885:1883 -p 8083:8083 -p 8084:8084 -p 8883:8883 -p 18085:18083 emqx/emqx:latest
# # sudo docker restart emqx
sleep 1
java -jar mqtt.jar 1885 &
sleep 1
python3 main.py emqx
sudo docker stop emqx
sudo pkill -9 -f mqtt.jar

# Interactive version for debugging
# # sudo docker run --name ejabberd -it -v $(pwd)/conf/ejabberd.yml:/opt/ejabberd/conf/ejabberd.yml -p 1886:1883 -p 5222:5222 docker.io/ejabberd/ecs live
sudo docker run --name ejabberd --detach -v $(pwd)/conf/ejabberd.yml:/opt/ejabberd/conf/ejabberd.yml -p 1886:1883 -p 5222:5222 docker.io/ejabberd/ecs
sleep 1
java -jar mqtt.jar 1886 &
sleep 1
python3 main.py ejabberd
sudo docker stop ejabberd
sudo pkill -9 -f mqtt.jar

sudo docker run -p 1887:1883 -e "DOCKER_VERNEMQ_ACCEPT_EULA=yes" -e "DOCKER_VERNEMQ_ALLOW_ANONYMOUS=on" --name vernemq1 -d vernemq/vernemq
sleep 1
java -jar mqtt.jar 1887 &
sleep 1
python3 main.py vernemq1
sudo docker stop vernemq1
sudo pkill -9 -f mqtt.jar

# ##### troubles here #####
# # has to be run in background
# sudo docker run --detach --name volantmq -p 1888:1883 -p 8080:8080 $(pwd)/examples/config.yaml:/etc/volantmq/config.yaml --env VOLANTMQ_CONFIG=/etc/volantmq/config.yaml volantmq/volantmq
# sleep 1
# java -jar mqtt.jar 1888 &
# sleep 1
# python3 main.py volantmq
# sudo docker stop volantmq 
# sudo pkill -9 -f mqtt.jar

# ##### troubles here #####
# sudo docker run --detach --name activemq -p 1889:1883 -p 8161:8161 --rm apache/activemq-artemis:latest-alpine

# sudo docker run --detach --name activemq -p 1889:1883 -p 61616:61616 -p 8161:8161 apache/activemq-artemis:latest-alpine

# sleep 1
# java -jar /home/paul/Downloads/AK-ITSipython3 main.py gmqttcherheit-ass2/assignment2/assignment2.jar 1889 &
# sleep 1
# python3 main.py activemq
# sudo docker stop activemq 
# sudo pkill -9 -f mqtt.jar

(&>/dev/null mosquitto -p 1883 &) # run in background without prints
java -jar mqtt.jar 1883 &
python3 main.py mosquitto
sudo pkill -9 -f mqtt.jar
sudo pkill -9 -f mosquitto


# go run . ~/Downloads/gmqtt/cmd/gmqttd/start -c default_config.yml &
# sleep 1
# java -jar mqtt.jar 1890 &
# sleep 1
# python3 main.py gmqtt
# sudo pkill -9 -f mqtt.jar
# sudo pkill -9 -f gmtqq


# needs to be run in folder
# cd ~/Downloads/apache-artemis-2.40.0/bin
"/home/paul/Downloads/apache-artemis-2.40.0/bin/bin/artemis" run &
sleep 1
java -jar mqtt.jar 1883 &
sleep 1
python3 main.py active-mq-artemis
sudo pkill -9 -f mqtt.jar
sudo pkill -9 -f artemis

# print who is using port
# sudo ss -lptn 'sport = :1883'
# kill PID
# sudo kill -9 PID
# kill by name
# sudo pkill -9 -f NAME
