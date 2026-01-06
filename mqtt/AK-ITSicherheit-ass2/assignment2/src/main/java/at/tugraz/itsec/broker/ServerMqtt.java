package at.tugraz.itsec.broker;

import java.io.IOException;
import java.net.InetAddress;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.function.Function;

import at.tugraz.itsec.client.data.MQTTBrokerAdapterConfig;
import at.tugraz.itsec.client.data.MQTTMessage;
import at.tugraz.itsec.client.data.TopicSubscription;
import at.tugraz.itsec.client.mqtt.MQTTClient;
import at.tugraz.itsec.client.mqtt.PacketFormatters;
import at.tugraz.itsec.client.packets.BrokerPacket;
import py4j.GatewayServer;

public class ServerMqtt {
	private int PORT = -1;
	private static String HOST = "127.0.0.1";
    MQTTClient client;

    private static Function<BrokerPacket, String> formatter = (BrokerPacket packet) -> {
        switch (packet.getPacketType()) {
            default:
                return packet.getPacketType().toString();
        }
    };

    public ServerMqtt(int port) throws IOException{
        PORT = port;
        MQTTBrokerAdapterConfig brokerConfig = new MQTTBrokerAdapterConfig(InetAddress.getByName(HOST), PORT, 1000, true,
                true, true);
        this.client = new MQTTClient("c0", "client0", null, brokerConfig, new PacketFormatters(formatter), 2);
    }


	public String connect() throws IOException {
		this.client.connectToBroker(true);
		return this.client.readIncoming();
	}

    public String disconnect() throws IOException {
        this.client.disconnectFromBroker();
        return this.client.readIncoming();
    }

    public String publish(String topicName, String msg, boolean dup) throws IOException {
        MQTTMessage message = new MQTTMessage(topicName, msg, (byte) 1, true);
        this.client.publish(message, dup); //dup
        return this.client.readIncoming();
    }

    // not clear how to build topicsubscription list
    public String subscribe(String topicName) throws IOException {
        TopicSubscription topic = new TopicSubscription(topicName, (byte) 1, false, true,
                    TopicSubscription.RetainHandling.ALWAYS);
        List<TopicSubscription> subscriptions = Collections.singletonList(topic);
        this.client.subscribe(subscriptions);
        return this.client.readIncoming();
    }

    public String unsubscribe(String topicFilters) throws IOException {
        this.client.unsubscribe(Arrays.asList(topicFilters));
        return this.client.readIncoming();
    }

    public static void main(String[] args) throws IOException {

        try {
            int port = Integer.parseInt(args[0]);
            ServerMqtt app = new ServerMqtt(port);
            // app is now the gateway.entry_point
            GatewayServer server = new GatewayServer(app);
            server.start();
            
            System.out.print("Running on port ");
            System.out.println(port);
        } catch (NumberFormatException e) {
            assert false;
        }
    }
}