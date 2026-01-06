package at.tugraz.itsec.client.packets;

import at.tugraz.itsec.client.data.PacketType;
import at.tugraz.itsec.client.data.VariableHeaderProperties;

public class PubCompPacket extends PubAckPacket {
    public PubCompPacket(int packetIdentifier) {
        super(packetIdentifier);
    }

    public PubCompPacket(int packetIdentifier, byte reasonCode, VariableHeaderProperties properties) {
        super(packetIdentifier, reasonCode, properties);
    }

    @Override
    public PacketType getPacketType() {
        return PacketType.PUBCOMP;
    }
}
