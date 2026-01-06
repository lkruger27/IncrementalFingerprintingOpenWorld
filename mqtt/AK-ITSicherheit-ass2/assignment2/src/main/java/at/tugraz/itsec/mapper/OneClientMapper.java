package at.tugraz.itsec.mapper;

import java.io.IOException;
import java.lang.reflect.Method;
import java.net.UnknownHostException;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;

import at.tugraz.itsec.client.data.MQTTBrokerAdapterConfig;
import at.tugraz.itsec.sut.MqttBrokerWrapper;
import at.tugraz.itsec.sut.MqttClientWrapper;
import de.learnlib.drivers.reflect.ConcreteMethodInput;
import de.learnlib.drivers.reflect.MethodInput;
import de.learnlib.drivers.reflect.ReturnValue;
import de.learnlib.mapper.api.SULMapper;

public class OneClientMapper implements SULMapper<String, String, ConcreteMethodInput, Object> {

	private MqttClientWrapper client;
	private MqttBrokerWrapper broker;
	
	private Method mConnect;
	

	public OneClientMapper(MQTTBrokerAdapterConfig brokerConfig) throws UnknownHostException, NoSuchMethodException, SecurityException {
		super();
		this.client = new MqttClientWrapper("c0", "client0", brokerConfig);
		this.broker = new MqttBrokerWrapper();
		mConnect = MqttBrokerWrapper.class.getMethod("connect", MqttClientWrapper.class);
		// TODO: add remaining methods: disconnect, subscribe, unsubscribe, publish

	}

	@Override
	public void pre() {
		SULMapper.super.pre();
	}

	@Override
	public void post() {
		try {
			client.reset();
		} catch (IOException e) {
			e.printStackTrace();
		}
	}

	public ConcreteMethodInput mapInput(String abstractInput) {	
		// TODO: handle other abstracted inputs and call the correct concrete input
		if(abstractInput == "connect") {
			return getConcreteMethod("connect", mConnect, Collections.singletonList(client));
		} else {
            throw new IllegalStateException("Unexpected value: " + abstractInput);
		}
	}

	public String mapOutput(Object concreteOutput) {
		return new ReturnValue(concreteOutput).toString();
	}
	
	private ConcreteMethodInput getConcreteMethod(String name, Method method, List<Object> params){
        MethodInput mi = new MethodInput(name, method, new HashMap<>(), params.toArray());
        return new ConcreteMethodInput(mi, new HashMap<>(), broker);
    }

}
