package at.tugraz.itsec.client.packets;

import at.tugraz.itsec.client.data.PacketType;
import at.tugraz.itsec.client.data.VariableHeaderProperties;

public interface MQTTControlPacket {
    PacketType getPacketType();

    default void checkProperties(VariableHeaderProperties properties) throws IllegalArgumentException {
        if (properties != null && !properties.validForPacketType(getPacketType())) {
            throw new IllegalArgumentException(String.format("Invalid properties for %s packet", getPacketType().toString()));
        }
    }
}