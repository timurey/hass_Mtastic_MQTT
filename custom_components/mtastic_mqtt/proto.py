"""Protobuf message conversion utilities."""
from __future__ import annotations

from typing import Any, Callable, Tuple
from .protobuf import mesh_pb2, mqtt_pb2, portnums_pb2, telemetry_pb2

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

import base64
import logging

_LOGGER = logging.getLogger(__name__)

DEFAULT_ENC_KEY = "1PG7OiApB1nwvP+rz05pAQ=="


def _as_position(obj: mesh_pb2.Position, envelope: mqtt_pb2.ServiceEnvelope) -> Tuple[str, dict[str, Any]]:
    """Convert Position protobuf to dict."""
    return ("position", {
        "latitude_i": obj.latitude_i,
        "longitude_i": obj.longitude_i,
        "altitude": obj.altitude,
        "ground_speed": obj.ground_speed,
        "sats_in_view": obj.sats_in_view,
    })


def _as_telemetry(obj: telemetry_pb2.Telemetry, envelope: mqtt_pb2.ServiceEnvelope) -> Tuple[str | None, dict[str, Any]]:
    """Convert Telemetry protobuf to dict."""
    type_ = obj.WhichOneof("variant")
    _LOGGER.debug("Telemetry variant: %s", type_)
    
    if type_ == "device_metrics":
        return ("device_metrics", {
            "battery_level": obj.device_metrics.battery_level,
            "voltage": obj.device_metrics.voltage,
            "channel_utilization": obj.device_metrics.channel_utilization,
            "air_util_tx": obj.device_metrics.air_util_tx,
        })
    elif type_ == "environment_metrics":
        return ("environment_metrics", {
            "temperature": obj.environment_metrics.temperature,
            "relative_humidity": obj.environment_metrics.relative_humidity,
            "barometric_pressure": obj.environment_metrics.barometric_pressure,
            "gas_resistance": obj.environment_metrics.gas_resistance,
            "radiation": obj.environment_metrics.radiation,
        })
    elif type_ == "power_metrics":
        return ("power_metrics", {
            "ch1_voltage": obj.power_metrics.ch1_voltage,
            "ch1_current": obj.power_metrics.ch1_current,
            "ch2_voltage": obj.power_metrics.ch2_voltage,
            "ch2_current": obj.power_metrics.ch2_current,
            "ch3_voltage": obj.power_metrics.ch3_voltage,
            "ch3_current": obj.power_metrics.ch3_current,
            "ch4_voltage": obj.power_metrics.ch4_voltage,
            "ch4_current": obj.power_metrics.ch4_current,
            "ch5_voltage": obj.power_metrics.ch5_voltage,
            "ch5_current": obj.power_metrics.ch5_current,
            "ch6_voltage": obj.power_metrics.ch6_voltage,
            "ch6_current": obj.power_metrics.ch6_current,
            "ch7_voltage": obj.power_metrics.ch7_voltage,
            "ch7_current": obj.power_metrics.ch7_current,
            "ch8_voltage": obj.power_metrics.ch8_voltage,
            "ch8_current": obj.power_metrics.ch8_current,
        })
    return (None, {})


def _as_node_info(obj: mesh_pb2.User, envelope: mqtt_pb2.ServiceEnvelope) -> Tuple[str, dict[str, Any]]:
    """Convert User (node info) protobuf to dict."""
    return ("nodeinfo", {
        "id": obj.id,
        "shortname": obj.short_name,
        "longname": obj.long_name,
    })


def _as_neighbor_info(obj: mesh_pb2.NeighborInfo, envelope: mqtt_pb2.ServiceEnvelope) -> Tuple[str, dict[str, Any]]:
    """Convert NeighborInfo protobuf to dict."""
    payload: dict[str, Any] = {
        "neighbors": [{"node_id": n.node_id, "snr": n.snr} for n in obj.neighbors],
    }
    payload["neighbors_count"] = len(obj.neighbors)
    return ("neighborinfo", payload)


def _as_text_message(obj: str, envelope: mqtt_pb2.ServiceEnvelope) -> Tuple[str, dict[str, Any]]:
    """Convert text message to dict."""
    return ("text_message", {
        "text": obj,
        "rx_time": envelope.packet.rx_time,
    })


_converters: dict[int, Tuple[type | None, Callable[[Any, mqtt_pb2.ServiceEnvelope], Tuple[str | None, dict[str, Any]]]]] = {
    portnums_pb2.POSITION_APP: (mesh_pb2.Position, _as_position),
    portnums_pb2.TELEMETRY_APP: (telemetry_pb2.Telemetry, _as_telemetry),
    portnums_pb2.NODEINFO_APP: (mesh_pb2.User, _as_node_info),
    portnums_pb2.NEIGHBORINFO_APP: (mesh_pb2.NeighborInfo, _as_neighbor_info),
    portnums_pb2.TEXT_MESSAGE_APP: (None, _as_text_message),
}


def convert_envelope_to_json(envelope: mqtt_pb2.ServiceEnvelope) -> dict[str, Any]:
    """Convert ServiceEnvelope protobuf to JSON-serializable dict."""
    result: dict[str, Any] = {
        "from": getattr(envelope.packet, "from"),
        "sender": envelope.gateway_id,
    }
    
    if not envelope.packet.HasField("decoded"):
        _LOGGER.debug("Envelope packet has no decoded field")
        return result
    
    portnum = envelope.packet.decoded.portnum
    if portnum not in _converters:
        _LOGGER.debug("Unsupported portnum: %d", portnum)
        return result
    
    config = _converters[portnum]
    proto_class, converter_func = config
    
    try:
        if proto_class:
            obj = proto_class()
            obj.ParseFromString(envelope.packet.decoded.payload)
            _LOGGER.debug("Parsed protobuf object: %s", obj)
        else:
            obj = envelope.packet.decoded.payload.decode("utf-8")
        
        type_, payload = converter_func(obj, envelope)
        _LOGGER.debug("Converted result: type=%s, payload=%s", type_, payload)
        
        if type_ and payload:
            result.update({
                "type": type_,
                "payload": payload,
            })
    except Exception as err:
        _LOGGER.exception("Error converting envelope for portnum %d: %s", portnum, err)
    
    return result


def try_encrypt_envelope(envelope: mqtt_pb2.ServiceEnvelope, key_b64: str) -> None:
    """Decrypt encrypted envelope packet."""
    try:
        # Normalize base64 key format
        key_b64_normalized = key_b64.replace("_", "/").replace("-", "+").encode("ascii")
        key_bytes = base64.b64decode(key_b64_normalized)
        
        # Check for default key indicator
        if len(key_bytes) == 1 and key_bytes[0] == 0x01:
            key_bytes = base64.b64decode(DEFAULT_ENC_KEY.encode("ascii"))
        
        if len(key_bytes) != 16:
            raise ValueError(f"Invalid key length: {len(key_bytes)}, expected 16 bytes")
        
        # Build nonce from packet ID and source node ID
        packet_id = getattr(envelope.packet, "id")
        from_node = getattr(envelope.packet, "from")
        nonce_packet_id = packet_id.to_bytes(8, "little")
        nonce_from_node = from_node.to_bytes(8, "little")
        nonce = nonce_packet_id + nonce_from_node
        
        if len(nonce) != 16:
            raise ValueError(f"Invalid nonce length: {len(nonce)}, expected 16 bytes")
        
        # Decrypt
        cipher = Cipher(
            algorithms.AES(key_bytes),
            modes.CTR(nonce),
            backend=default_backend(),
        )
        decryptor = cipher.decryptor()
        encrypted_data = getattr(envelope.packet, "encrypted")
        decrypted_bytes = decryptor.update(encrypted_data) + decryptor.finalize()
        
        # Parse decrypted data
        data = mesh_pb2.Data()
        data.ParseFromString(decrypted_bytes)
        envelope.packet.decoded.CopyFrom(data)
        
        _LOGGER.debug("Successfully decrypted envelope packet")
        
    except Exception as err:
        _LOGGER.error("Failed to decrypt envelope: %s", err)
        raise
