package at.tugraz.itsec.client.packets;

import at.tugraz.itsec.client.utils.MQTTUtils;

import java.util.List;

public interface ClientPacket extends MQTTControlPacket {
    default List<Byte> toBinary() {
        return MQTTUtils.encodeFixedHeader(getPacketType(), (byte) 0, 0);
    }
}
