package at.tugraz.itsec.sut;

import java.io.IOException;

public class MqttBrokerWrapper {

	public MqttBrokerWrapper() {
		super();
	}

	public String connect(MqttClientWrapper client) throws IOException {
		return client.connect();
	}
	
	public String disconnect(MqttClientWrapper client) throws IOException {
		return client.disconnect();
	}
	
	public String subscribe(MqttClientWrapper client, String topicName) throws IOException {
		return client.subscribe(topicName);
	}
	
	public String unsubscribe(MqttClientWrapper client, String topicName) throws IOException {
		return client.unsubscribe(topicName);
	}
	
	public String publish(MqttClientWrapper client, String topicName, String msg) throws IOException {
		return client.publish(topicName, msg);
	}
	
}
