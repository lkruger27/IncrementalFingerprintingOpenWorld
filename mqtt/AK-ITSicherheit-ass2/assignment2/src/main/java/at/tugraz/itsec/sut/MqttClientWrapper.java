package at.tugraz.itsec.sut;

import java.io.IOException;

import java.util.function.Function;

import at.tugraz.itsec.client.data.MQTTBrokerAdapterConfig;
import at.tugraz.itsec.client.mqtt.MQTTClient;
import at.tugraz.itsec.client.mqtt.PacketFormatters;
import at.tugraz.itsec.client.packets.BrokerPacket;
public class MqttClientWrapper {

	private static Function<BrokerPacket, String> formatter = (BrokerPacket packet) -> {
		switch (packet.getPacketType()) {
		default:
			return packet.getPacketType().toString();
		}
	};
	
	MQTTClient client;
	
	public MqttClientWrapper(String id, String userName, MQTTBrokerAdapterConfig config) {
		super();
		this.client = new MQTTClient(id, userName, null, config, new PacketFormatters(formatter), 1);	
	}

	public String connect() throws IOException {
		client.connectToBroker(true);
		return readIncoming();
	}
	
	public String disconnect() throws IOException {
		// TODO: implement
		return null;
	}
	
	public String subscribe(String topicName) throws IOException {
		// TODO: implement
		return null;
	}
	
	public String unsubscribe(String topicName) throws IOException {
		// TODO: implement
		return null;
	}

	public void reset() throws IOException {
		client.resetAndDisconnect();
		client.closeTCPSession();
	}
	
	public String publish(String topicName, String message) throws IOException {
		// TODO: implement
		return null;
	}
	
	public String readIncoming() throws IOException {
		return client.readIncoming();
	}

}
