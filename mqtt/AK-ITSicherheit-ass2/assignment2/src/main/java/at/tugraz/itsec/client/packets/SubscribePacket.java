package at.tugraz.itsec.client.packets;

import at.tugraz.itsec.client.data.PacketType;
import at.tugraz.itsec.client.data.TopicSubscription;
import at.tugraz.itsec.client.data.VariableHeaderProperties;
import at.tugraz.itsec.client.utils.MQTTUtils;

import java.util.ArrayList;
import java.util.List;

public class SubscribePacket implements ClientPacket {
    private int packetIdentifier;
    private VariableHeaderProperties properties;
    private List<TopicSubscription> topicSubscriptions;

    public SubscribePacket(int packetIdentifier, VariableHeaderProperties properties, List<TopicSubscription> topicSubscriptions) {
        checkProperties(properties);

        this.packetIdentifier = packetIdentifier;
        this.properties = (properties == null) ? new VariableHeaderProperties() : properties;
        this.topicSubscriptions =  (topicSubscriptions == null) ? new ArrayList<>() : topicSubscriptions;
    }

    @Override
    public List<Byte> toBinary() {
        List<Byte> data = new ArrayList<>();

        // Variable Header
        data.add((byte)((packetIdentifier >>> 8) & 0xFF));
        data.add((byte)(packetIdentifier & 0xFF));
        data.addAll(properties.toBinary());

        // Payload
        topicSubscriptions.forEach(ts -> data.addAll(ts.toBinary()));

        // Fixed Header at beginning
        data.addAll(0, MQTTUtils.encodeFixedHeader(getPacketType(), (byte) 0b0010, data.size()));

        return data;
    }

    @Override
    public PacketType getPacketType() {
        return PacketType.SUBSCRIBE;
    }
}
