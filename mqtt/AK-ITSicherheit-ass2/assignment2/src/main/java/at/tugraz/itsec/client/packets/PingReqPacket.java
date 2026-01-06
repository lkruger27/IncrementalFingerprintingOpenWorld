package at.tugraz.itsec.client.packets;

import at.tugraz.itsec.client.data.PacketType;

public class PingReqPacket implements ClientPacket {
    @Override
    public PacketType getPacketType() {
        return PacketType.PINGREQ;
    }
}
