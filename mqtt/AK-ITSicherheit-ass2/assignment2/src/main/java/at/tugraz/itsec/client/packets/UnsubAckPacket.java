package at.tugraz.itsec.client.packets;

import at.tugraz.itsec.client.data.PacketType;
import at.tugraz.itsec.client.data.VariableHeaderProperties;

import java.util.List;

public class UnsubAckPacket extends SubAckPacket {
    public UnsubAckPacket(int packetIdentifier, VariableHeaderProperties properties, List<Byte> reasonCodes) {
        super(packetIdentifier, properties, reasonCodes);
    }
    @Override
    public PacketType getPacketType() {
        return PacketType.UNSUBACK;
    }
}
