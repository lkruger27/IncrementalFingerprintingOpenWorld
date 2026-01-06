package at.tugraz.itsec.client.packets;

import at.tugraz.itsec.client.data.PacketType;
import at.tugraz.itsec.client.data.VariableHeaderProperties;

public class PubRecPacket extends PubAckPacket {
    public PubRecPacket(int packetIdentifier) {
        super(packetIdentifier);
    }

    public PubRecPacket(int packetIdentifier, byte reasonCode, VariableHeaderProperties properties) {
        super(packetIdentifier, reasonCode, properties);
    }

    @Override
    public PacketType getPacketType() {
        return PacketType.PUBREC;
    }
}
