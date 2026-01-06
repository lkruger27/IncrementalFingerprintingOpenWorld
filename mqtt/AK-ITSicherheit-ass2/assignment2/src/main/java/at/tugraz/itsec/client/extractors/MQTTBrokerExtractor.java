package at.tugraz.itsec.client.extractors;

import at.tugraz.itsec.client.data.VariableHeaderProperties;
import at.tugraz.itsec.client.packets.BrokerPacket;
import at.tugraz.itsec.client.utils.MQTTUtils;

import java.nio.ByteBuffer;

public interface MQTTBrokerExtractor {
    BrokerPacket extract(FixedHeader fixedHeader, ByteBuffer data);

    default VariableHeaderProperties extractProperties(FixedHeader fixedHeader, ByteBuffer data, int bytesBeforeProperties, boolean hasPayload) {
        int expectedRemainingLength = bytesBeforeProperties - data.position();
        int propertiesLength = MQTTUtils.decodeVariableByteInteger(data);
        expectedRemainingLength += data.position() + propertiesLength;

        if (!hasPayload && fixedHeader.getRemainingLength() != expectedRemainingLength)
            throw new IllegalArgumentException(String.format("Malformed Packet. Expected remaining length of %d, but got %d", expectedRemainingLength, fixedHeader.getRemainingLength()));

        return VariableHeaderProperties.parseVariableHeaderProperties(data, propertiesLength);
    }
}
