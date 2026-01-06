import paho.mqtt.client as mqtt

from aalpy.base import SUL
from aalpy.oracles import RandomWalkEqOracle
from aalpy.learning_algs import run_Lstar
from aalpy.learning_algs.adaptive import AdaptiveLSharp
from py4j.java_gateway import JavaGateway
import pandas as pd

import argparse
import random
import string

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, reason_code, properties):
    pass
    # print(f"Connected with result code {reason_code}")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    # client.subscribe("$SYS/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

input_al = ["connect", "disconnect", "publish", "subscribe", "unsubscribe"] # "invalid"

# class MQTT_SUL(SUL):
#     def __init__(self, version, protocol_version):
#         self.num_queries = 0
#         self.num_steps = 0
#         self.state = 'CONCLOSED'
#         self.topics = set()
        
#         self.version = version
#         self.protocol_version = protocol_version
        
#     def pre(self):
#         self.state = 'CONCLOSED'
#         if self.protocol_version == mqtt.MQTTProtocolVersion.MQTTv5:
#             self.mqttc = mqtt.Client(self.version, protocol=self.protocol_version)
#         else:
#             self.mqttc = mqtt.Client(self.version, clean_session=True, protocol=self.protocol_version)
            
#         self.mqttc.on_connect = on_connect
#         self.mqttc.on_message = on_message
        
#         # r = self.mqttc.connect("localhost", 1885, 90)
#         # self.mqttc.loop()
#         # print(r, self.mqttc._state)
        
#         # r = self.mqttc.connect("localhost", 1885, 90)
#         # self.mqttc.loop(10)
#         # print(r, self.mqttc._state)
        
#         # assert False
        
#     def post(self):
#         self.topics.clear()
#         # self.mqttc.reinitialise()
#         # del self.mqttc
#         # self.mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

#     def step(self, letter):
#         topic = ''.join(random.choices(string.ascii_uppercase + string.digits + '\\', k=5)) # "$SYS/#"
#         if letter == 'connect':
#             print("connect")
#             if self.protocol_version == mqtt.MQTTProtocolVersion.MQTTv5:
#                 r = self.mqttc.connect("localhost", 1885, 90)
#             else:
#                 r = self.mqttc.connect("localhost", 1885, 90)
#             # self.mqttc.loop()
            
#             print("returned", r)
#             return self.mqttc._state
#             return r
#         elif letter == 'disconnect':
#             print("disconnect")
#             r = self.mqttc.disconnect()
#             print("returned", r)
#             return self.mqttc._state
#             return r
#         elif letter == 'publish':
#             print("publish")
#             r = self.mqttc.publish(topic, "test")[0]
#             print("returned", r)
#             return self.mqttc._state
#             return r
#         elif letter == 'subscribe':
#             print("subscribe")
#             r = self.mqttc.subscribe(topic)[0]
#             print("returned", r)
#             return self.mqttc._state
#             return r
#         elif letter == 'unsubscribe':
#             print("unsubscribe")
#             r = self.mqttc.unsubscribe(topic)[0]
#             print("returned", r)
#             return self.mqttc._state
#             return r
#         else:
#             return self.mqttc.unsubscribe(topic)
   

class JAVA_MQTT_SUL(SUL):
    def __init__(self):
        self.num_queries = 0
        self.num_steps = 0
        self.state = 'CONCLOSED'
        self.topics = set()
        self.duplicate = False
        
    def pre(self):
        self.state = 'CONCLOSED'
        self.gateway = JavaGateway()
        self.app = self.gateway.entry_point
        
    def post(self):
        self.topics.clear()
        self.app.disconnect()
        # if self.app:
        #     self.app.disconnect()
        # # self.app.gateway.sho
        # if self.gateway:
        #     del self.gateway
        # if self.app:
        #     del self.app

    def step(self, letter):
        topic = "/test"
        if args and args.debug:
            print(letter)
        if letter == 'connect':
            return self.app.connect()
        elif letter == 'disconnect':
            return self.app.disconnect()
        elif letter == 'publish':
            msg = "test"
            r = self.app.publish(topic, msg, self.duplicate)
            if args.debug:
                print("r", '__'.join(set(r.split("__"))))
            self.duplicate = True
            return r
        elif letter == 'subscribe':
            return self.app.subscribe(topic)
        elif letter == 'unsubscribe':
            string_class = self.gateway.jvm.String
            string_array = self.gateway.new_array(string_class, 1, 1)
            string_array[0][0] = topic
            return self.app.unsubscribe(topic)
        else:
            assert False
            
if __name__ == '__main__':
    
    parser = argparse.ArgumentParser("simple_example")
    parser.add_argument("broker", help="Broker currently testing.", type=str)
    parser.add_argument("--new_file", help="Should a new file be created?", default=False, action='store_true')
    parser.add_argument("--debug", help="Print additional debug information", default=False, action='store_true')
    args = parser.parse_args()

    # gateway = JavaGateway()
    # app = gateway.entry_point
    # print(app.connect())
    # print(app.subscribe("/test"))
    # # print(app.disconnect())
    # # print(app.unsubscribe())
    # # print(app.publish())
    
    
    # import paho.mqtt.client as mqtt

    # # The callback for when the client receives a CONNACK response from the server.
    # def on_connect(client, userdata, flags, reason_code, properties):
    #     print(f"Connected with result code {reason_code}")
    #     # Subscribing in on_connect() means that if we lose the connection and
    #     # reconnect then subscriptions will be renewed.
    #     client.subscribe("$SYS/#")

    # # The callback for when a PUBLISH message is received from the server.
    # def on_message(client, userdata, msg):
    #     print(msg.topic+" "+str(msg.payload))

    # mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    # mqttc.on_connect = on_connect
    # mqttc.on_message = on_message

    # print(mqttc.connect("127.0.0.1", 1883, 5))
    # print(mqttc.subscribe('/test')[0])
    # print(mqttc.publish('/test', 'test')[0])

    # # Blocking call that processes network traffic, dispatches callbacks and
    # # handles reconnecting.
    # # Other loop*() functions are available that give a threaded interface and a
    # # manual interface.
    # mqttc.loop_forever()

    # assert(False)

    result_dict =  {'learning_rounds': [], 'automaton_size': [], 'queries_learning': [], 'steps_learning': [], 'queries_eq_oracle': [], 'steps_eq_oracle': [], 'learning_time': [], 'eq_oracle_time': [], 'total_time': [], 'cache_saved': [], 'broker': [], 'alg': []}
    sul = JAVA_MQTT_SUL()
    eq_oracle = RandomWalkEqOracle(input_al, sul, num_steps=2000, reset_after_cex=True, reset_prob=0.15)
    m1, run_infos = run_Lstar(input_al, sul, eq_oracle=eq_oracle, automaton_type='mealy', cache_and_non_det_check=True,
                      print_level=3, return_data=True)
    for k in run_infos:
        if k in result_dict:
            result_dict[k].append(run_infos[k])
    result_dict['broker'].append(f'{args.broker}')
    result_dict['alg'].append('L*')
    m1.save(f'out/{args.broker}-L*',file_type='pdf')
    
    sul = JAVA_MQTT_SUL()
    eq_oracle = RandomWalkEqOracle(input_al, sul, num_steps=2000, reset_after_cex=True, reset_prob=0.15)
    m2, run_infos = AdaptiveLSharp.run_adaptive_Lsharp(input_al, sul, [], eq_oracle=eq_oracle, automaton_type='mealy', cache_and_non_det_check=True,
                      print_level=3, return_data=True)
    for k in run_infos:
        if k in result_dict:
            result_dict[k].append(run_infos[k])
    result_dict['broker'].append(f'{args.broker}')
    result_dict['alg'].append('L#')
    m2.save(f'out/{args.broker}-L#',file_type='pdf')
    print(m2, run_infos)
    
    # sul = MQTT_SUL(mqtt.CallbackAPIVersion.VERSION2, mqtt.MQTTProtocolVersion.MQTTv5)
    # m2 = AdaptiveLSharp.run_adaptive_Lsharp(input_al, sul, [], eq_oracle=eq_oracle, automaton_type='mealy', cache_and_non_det_check=True,
    #                   print_level=3)
    # m2.visualize("m2",file_type='dot')

    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a
    # manual interface.
    # mqttc.loop_forever()
    
    print(result_dict)
    if args.new_file:
        pd.DataFrame.from_dict(result_dict).to_csv('results.csv', header=True)
    else:
        pd.DataFrame.from_dict(result_dict).to_csv('results.csv', mode='a', header=False)
    
# TODO:
# - Add more topics
# list of brokers https://github.com/pascaldekloe/mqtt/wiki/Brokers
# mqtt implementation (brokers and clients) https://en.wikipedia.org/wiki/Comparison_of_MQTT_implementations