# protocols.py — OXNET v2.0
# Pluggable header parsers so a single relay/transport can carry multiple
# proxy protocols. Currently supports VLESS and Trojan. Transport (WS / XHTTP)
# is orthogonal to protocol; the same /ws and /xhttp routes auto-detect which
# protocol a client is speaking from the first bytes it sends.
import hashlib

_HEX = b"0123456789abcdefABCDEF"


def parse_vless_header(chunk: bytes):
    """Return (command, address, port, remaining_payload) for a VLESS request."""
    if len(chunk) < 24:
        raise ValueError("vless chunk too small")
    pos = 1                       # protocol version
    pos += 16                     # 16-byte user id
    addon_len = chunk[pos]; pos += 1 + addon_len
    command = chunk[pos]; pos += 1
    port = int.from_bytes(chunk[pos:pos + 2], "big"); pos += 2
    addr_type = chunk[pos]; pos += 1
    if addr_type == 1:            # IPv4
        address = ".".join(str(b) for b in chunk[pos:pos + 4]); pos += 4
    elif addr_type == 2:          # domain
        dlen = chunk[pos]; pos += 1
        address = chunk[pos:pos + dlen].decode("utf-8", errors="ignore"); pos += dlen
    elif addr_type == 3:          # IPv6 (FIX: advance pos by the full 16 bytes)
        ab = chunk[pos:pos + 16]; pos += 16
        address = ":".join(f"{ab[i]:02x}{ab[i + 1]:02x}" for i in range(0, 16, 2))
    else:
        raise ValueError(f"unknown vless addr type: {addr_type}")
    return command, address, port, chunk[pos:]


def parse_trojan_header(chunk: bytes):
    """Return (password_hash_hex, command, address, port, payload) for Trojan."""
    if len(chunk) < 60:
        raise ValueError("trojan chunk too small")
    if chunk[56:58] != b"\r\n":
        raise ValueError("bad trojan header")
    pw_hash = chunk[:56].decode("ascii", errors="ignore")
    pos = 58
    command = chunk[pos]; pos += 1               # 1=connect, 3=udp
    atyp = chunk[pos]; pos += 1
    if atyp == 1:                                 # IPv4
        address = ".".join(str(b) for b in chunk[pos:pos + 4]); pos += 4
    elif atyp == 3:                               # domain
        dlen = chunk[pos]; pos += 1
        address = chunk[pos:pos + dlen].decode("utf-8", errors="ignore"); pos += dlen
    elif atyp == 4:                               # IPv6
        ab = chunk[pos:pos + 16]; pos += 16
        address = ":".join(f"{ab[i]:02x}{ab[i + 1]:02x}" for i in range(0, 16, 2))
    else:
        raise ValueError(f"unknown trojan addr type: {atyp}")
    port = int.from_bytes(chunk[pos:pos + 2], "big"); pos += 2
    if chunk[pos:pos + 2] == b"\r\n":
        pos += 2
    return pw_hash, command, address, port, chunk[pos:]


def detect_protocol(chunk: bytes) -> str:
    """Cheap first-bytes sniff. Trojan opens with 56 hex chars + CRLF."""
    if len(chunk) >= 58 and chunk[56:58] == b"\r\n" and all(c in _HEX for c in chunk[:56]):
        return "trojan"
    return "vless"


def trojan_password_hash(password: str) -> str:
    return hashlib.sha224(password.encode("utf-8")).hexdigest()


def parse_any_header(chunk: bytes, trojan_password: str | None = None) -> dict:
    """Detect + parse. When trojan_password is provided, Trojan auth is enforced.
    Returns a dict: proto, command, address, port, payload, resp_prefix.
    resp_prefix is the bytes to prepend to the first downstream packet
    (VLESS uses b"\x00\x00"; Trojan uses none)."""
    proto = detect_protocol(chunk)
    if proto == "trojan":
        pw_hash, command, address, port, payload = parse_trojan_header(chunk)
        if trojan_password is not None:
            if pw_hash.lower() != trojan_password_hash(trojan_password).lower():
                raise ValueError("trojan auth failed")
        return {"proto": "trojan", "command": command, "address": address,
                "port": port, "payload": payload, "resp_prefix": b""}
    command, address, port, payload = parse_vless_header(chunk)
    return {"proto": "vless", "command": command, "address": address,
            "port": port, "payload": payload, "resp_prefix": b"\x00\x00"}
