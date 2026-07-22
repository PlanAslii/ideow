# state.py — OXNET v2.0 core state
# Timezone-consistent, multi-protocol aware (VLESS + Trojan) core.
import asyncio
import json
import os
import hashlib
import secrets
import time
import tempfile
import aiofiles
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from collections import deque, defaultdict
from pathlib import Path
from urllib.parse import quote
import logging
from fastapi import Request

# ── Logger Setup ───────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("OXNET")

IRAN_TZ = ZoneInfo("Asia/Tehran")

# ── Smart Persistence Path ────────────
env_data = os.environ.get("DATA_DIR")
if env_data:
    DATA_DIR = Path(env_data)
else:
    _local_data = Path("./data")
    try:
        _local_data.mkdir(parents=True, exist_ok=True)
        _test_file = _local_data / ".write_test"
        _test_file.touch()
        _test_file.unlink()
        DATA_DIR = _local_data
    except (OSError, PermissionError):
        logger.warning("Directory './data' is not writable. Falling back to temporary directory.")
        DATA_DIR = Path(tempfile.gettempdir()) / "oxnet_data"
        DATA_DIR.mkdir(parents=True, exist_ok=True)

DATA_FILE = DATA_DIR / "oxnet_state.json"
SECRET_FILE = DATA_DIR / "oxnet_secret.key"
SAVE_LOCK = asyncio.Lock()


def _load_or_create_secret() -> str:
    env_secret = os.environ.get("SECRET_KEY")
    if env_secret:
        return env_secret
    try:
        if SECRET_FILE.exists():
            existing = SECRET_FILE.read_text(encoding="utf-8").strip()
            if existing:
                return existing
        new_secret = secrets.token_urlsafe(32)
        SECRET_FILE.write_text(new_secret, encoding="utf-8")
        return new_secret
    except Exception as e:
        logger.warning(f"Could not persist SECRET_KEY, sessions/password may reset on restart: {e}")
        return secrets.token_urlsafe(32)


CONFIG = {
    "port": int(os.environ.get("PORT", 8000)),
    "secret": _load_or_create_secret(),
    "api_key": os.environ.get("API_KEY", secrets.token_urlsafe(32)),
    "host": os.environ.get("RAILWAY_PUBLIC_DOMAIN", "localhost"),
}

PANEL_NAME = "OXNET"
PANEL_VERSION = "2.0"
XHTTP_BASE_PATH = os.environ.get("XHTTP_BASE_PATH", "/xhttp-oxnet").strip() or "/xhttp-oxnet"
if not XHTTP_BASE_PATH.startswith("/"):
    XHTTP_BASE_PATH = "/" + XHTTP_BASE_PATH

# ── Global State Variables ──────────────────────────────────
connections: dict = {}
stats = {
    "total_bytes": 0,
    "total_requests": 0,
    "total_errors": 0,
    "start_time": time.time(),
}
error_logs: deque = deque(maxlen=50)
activity_logs: deque = deque(maxlen=200)
hourly_traffic: dict = defaultdict(int)
http_client = None

LINKS: dict = {}
LINKS_LOCK = asyncio.Lock()
SUBS: dict = {}
SUBS_LOCK = asyncio.Lock()

# Protocols now include Trojan transports and the new multi-protocol bundle.
PROTOCOLS = (
    "multi-protocol",
    "multi-auto",
    "shadowsocks-ws",
    "shadowsocks-xhttp",
    "vless-ws",
    "vless-xhttp-packet-up",
    "vless-xhttp-stream-up",
    "trojan-ws",
    "trojan-xhttp-packet-up",
)
DEFAULT_PROTOCOL = "multi-protocol"
FINGERPRINTS = ("chrome", "firefox", "safari", "ios", "android", "edge", "360", "qq", "random", "randomized")
DEFAULT_FINGERPRINT = "chrome"
DEFAULT_ALPN_BY_PROTOCOL = {
    "multi-protocol": "h2,http/1.1",
    "multi-auto": "h2,http/1.1",
    "vless-ws": "http/1.1",
    "vless-xhttp-packet-up": "h2,http/1.1",
    "vless-xhttp-stream-up": "h2,http/1.1",
    "trojan-ws": "http/1.1",
    "trojan-xhttp-packet-up": "h2,http/1.1",
}
DEFAULT_PORT = 443
MIN_PORT, MAX_PORT = 1, 65535
DEFAULT_SPEED_LIMIT = 0


def hash_password(pw: str) -> str:
    return hashlib.sha256(f"{pw}{CONFIG['secret']}".encode()).hexdigest()


AUTH = {"password_hash": hash_password(os.environ.get("ADMIN_PASSWORD", "OXNET"))}
CONFIG["login_path"] = os.environ.get("LOGIN_PATH", "/login")
if not CONFIG["login_path"].startswith("/"): CONFIG["login_path"] = "/" + CONFIG["login_path"]
SESSIONS: dict = {}
SESSIONS_LOCK = asyncio.Lock()
SESSION_COOKIE = "oxnet_session"
SESSION_TTL = 60 * 60 * 24 * 365

# ── Helper Functions ──────────────────────────────────────
def now_ir() -> datetime:
    return datetime.now(IRAN_TZ)


def now_iso() -> str:
    """Timezone-aware ISO timestamp used everywhere for consistency."""
    return now_ir().isoformat()


def log_activity(kind: str, message: str, level: str = "info"):
    activity_logs.append({
        "kind": kind,
        "level": level,
        "message": message,
        "time": now_iso(),
    })


def uptime() -> str:
    secs = int(time.time() - stats["start_time"])
    h, m, s = secs // 3600, (secs % 3600) // 60, secs % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def parse_size_to_bytes(value: float, unit: str) -> int:
    unit = unit.upper()
    if unit == "GB": return int(value * 1024 ** 3)
    if unit == "MB": return int(value * 1024 ** 2)
    if unit == "KB": return int(value * 1024)
    return int(value)


def parse_speed_to_bytes(value: float, unit: str) -> int:
    if value <= 0:
        return 0
    unit = (unit or "MBIT").upper()
    if unit == "MBIT": return int(value * 1024 * 1024 / 8)
    if unit == "KB": return int(value * 1024)
    if unit == "MB": return int(value * 1024 * 1024)
    return int(value)


def is_link_expired(link: dict) -> bool:
    exp = link.get("expires_at")
    if not exp:
        return False
    try:
        dt = datetime.fromisoformat(exp)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=IRAN_TZ)
        return now_ir() > dt
    except Exception:
        return False


def is_link_allowed(link: dict | None) -> bool:
    if link is None:
        return False
    if not link.get("active", True):
        return False
    if is_link_expired(link):
        return False
    lb = link.get("limit_bytes", 0)
    if lb > 0 and link.get("used_bytes", 0) >= lb:
        return False
    return True


def fmt_bytes(b: int) -> str:
    if b < 1024: return f"{b} B"
    if b < 1024**2: return f"{b/1024:.1f} KB"
    if b < 1024**3: return f"{b/1024**2:.2f} MB"
    return f"{b/1024**3:.2f} GB"


def unique_ips_for_uuid(uuid: str) -> set:
    return {c.get("ip") for c in connections.values() if c.get("uuid") == uuid and c.get("ip")}


def is_ip_allowed(link: dict | None, uuid: str, ip: str) -> bool:
    if link is None:
        return False
    limit = int(link.get("ip_limit", 0) or 0)
    if limit <= 0:
        return True
    ips = unique_ips_for_uuid(uuid)
    if ip in ips:
        return True
    return len(ips) < limit


async def check_and_use(uid: str, n: int) -> bool:
    """Atomically verify a link is allowed and account traffic. Shared by all transports."""
    async with LINKS_LOCK:
        link = LINKS.get(uid)
        if link is None:
            return False
        if not is_link_allowed(link):
            return False
        link["used_bytes"] += n
        stats["total_bytes"] += n
        hourly_traffic[now_ir().strftime("%H:00")] += n
    return True


def get_host(request: Request | None = None) -> str:
    if request is not None:
        h = request.headers.get("x-forwarded-host") or request.headers.get("host")
        if h:
            h = h.split(":")[0]
            CONFIG["host"] = h
            return h
    return os.environ.get("RAILWAY_PUBLIC_DOMAIN", CONFIG["host"])


def generate_uuid() -> str:
    h = secrets.token_hex(16)
    return f"{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"


def sanitize_path_slug(value: str | None, fallback: str) -> str:
    """Return a safe single URL path segment for WS/XHTTP config paths."""
    raw = (value or fallback or "").strip().strip("/")
    raw = raw.split("/")[-1] if "/" in raw else raw
    safe = "".join(ch for ch in raw if ch.isalnum() or ch in ("-", "_", "."))
    return (safe or fallback).strip("/")


def link_path_key(uid: str, link: dict | None) -> str:
    return sanitize_path_slug((link or {}).get("path_slug"), uid)


def resolve_link_key(key: str) -> tuple[str | None, dict | None]:
    """Resolve either a real UUID or a custom admin path slug to the stored link."""
    if key in LINKS:
        return key, LINKS.get(key)
    for uid, link in LINKS.items():
        if link_path_key(uid, link) == key:
            return uid, link
    return None, None


def get_link_by_key(key: str) -> dict | None:
    return resolve_link_key(key)[1]


def is_path_slug_available(slug: str, current_uid: str | None = None) -> bool:
    slug = sanitize_path_slug(slug, current_uid or slug)
    for uid, link in LINKS.items():
        if current_uid and uid == current_uid:
            continue
        if uid == slug or link_path_key(uid, link) == slug:
            return False
    return True


def trojan_password(link: dict | None, uid: str) -> str:
    return (link or {}).get("secret") or uid.replace("-", "")


def _path_for_protocol(protocol: str, uuid: str, link: dict | None = None) -> tuple[str, str, str]:
    """Return client type, mode and path for the selected OXNET transport."""
    path_key = link_path_key(uuid, link)
    if "xhttp" in protocol:
        mode = protocol.split("xhttp-", 1)[1]
        return "xhttp", mode, f"{XHTTP_BASE_PATH}/{mode}/{path_key}"
    return "ws", "", f"/ws/{path_key}"


def _safe_port(port: int | None) -> int:
    try:
        port_val = int(port or DEFAULT_PORT)
    except (TypeError, ValueError):
        port_val = DEFAULT_PORT
    return port_val if (MIN_PORT <= port_val <= MAX_PORT) else DEFAULT_PORT


def _safe_fp(fingerprint: str | None) -> str:
    fp = (fingerprint or DEFAULT_FINGERPRINT).strip().lower() or DEFAULT_FINGERPRINT
    return fp if fp in FINGERPRINTS else DEFAULT_FINGERPRINT


def _alpn_for(protocol: str, alpn: str | None) -> str:
    return (alpn or "").strip() or DEFAULT_ALPN_BY_PROTOCOL.get(protocol, "http/1.1")


def generate_vless_link(uuid, host, remark="OXNET", protocol="vless-ws", fingerprint=None,
                        alpn=None, port=None, path_slug=None):
    """Generate a VLESS link where the user id stays UUID and only the transport path is editable."""
    if not protocol.startswith("vless-"):
        protocol = "vless-ws"
    fp = _safe_fp(fingerprint)
    alpn_val = _alpn_for(protocol, alpn)
    port_val = _safe_port(port)
    typ, mode, path = _path_for_protocol(protocol, uuid, {"path_slug": path_slug or uuid})
    params = {
        "encryption": "none",
        "security": "tls",
        "type": typ,
        "host": host,
        "path": path,
        "sni": host,
        "fp": fp,
        "alpn": alpn_val,
    }
    if typ == "xhttp":
        params["mode"] = mode
    query = "&".join(f"{k}={quote(str(v))}" for k, v in params.items() if v != "")
    return f"vless://{uuid}@{host}:{port_val}?{query}#{quote(remark)}"


def generate_trojan_link(password, host, remark="OXNET", protocol="trojan-ws", fingerprint=None,
                         alpn=None, port=None, path_slug=None):
    """Generate a Trojan link over WS/XHTTP with TLS."""
    if not protocol.startswith("trojan-"):
        protocol = "trojan-ws"
    fp = _safe_fp(fingerprint)
    alpn_val = _alpn_for(protocol, alpn)
    port_val = _safe_port(port)
    typ, mode, path = _path_for_protocol(protocol, path_slug or password, {"path_slug": path_slug})
    params = {
        "security": "tls",
        "type": typ,
        "host": host,
        "path": path,
        "sni": host,
        "fp": fp,
        "alpn": alpn_val,
    }
    if typ == "xhttp":
        params["mode"] = mode
    query = "&".join(f"{k}={quote(str(v))}" for k, v in params.items() if v != "")
    return f"trojan://{quote(password)}@{host}:{port_val}?{query}#{quote(remark)}"


def links_for_link(link: dict, uid: str, host: str) -> list[str]:
    """Generate working OXNET outputs for a config, honoring multi-protocol bundles."""
    proto = link.get("protocol", DEFAULT_PROTOCOL)
    remark = link.get("label") or "OXNET"
    fp = link.get("fingerprint") or DEFAULT_FINGERPRINT
    alpn = link.get("alpn") or ""
    port = link.get("port") or DEFAULT_PORT
    path_key = link_path_key(uid, link)
    pw = trojan_password(link, uid)

    def vless(p, tag):
        return generate_vless_link(uid, host, f"{remark}-{tag}", p, fp, alpn, port, path_key)

    def trojan(p, tag):
        return generate_trojan_link(pw, host, f"{remark}-{tag}", p, fp, alpn, port, path_key)

    if proto == "multi-protocol":
        return [
            vless("vless-ws", "VLESS-WS"),
            vless("vless-xhttp-packet-up", "VLESS-XHTTP"),
            vless("vless-xhttp-stream-up", "VLESS-XHTTP-STREAM"),
            trojan("trojan-ws", "TROJAN-WS"),
            trojan("trojan-xhttp-packet-up", "TROJAN-XHTTP"),
        ]
    if proto == "multi-auto":
        return [
            vless("vless-ws", "VLESS-WS"),
            vless("vless-xhttp-packet-up", "VLESS-XHTTP"),
        ]
    if proto.startswith("trojan-"):
        return [trojan(proto, remark)]
    if proto.startswith("vless-"):
        return [vless(proto, remark)]
    return [vless("vless-ws", remark)]


def vless_link_for_link(link: dict, uid: str, host: str) -> str:
    return links_for_link(link, uid, host)[0]


def primary_link_for_link(link: dict, uid: str, host: str) -> str:
    return links_for_link(link, uid, host)[0]


def subscription_text_for_link(link: dict, uid: str, host: str) -> str:
    return "\n".join(links_for_link(link, uid, host))


def client_ip(request: Request) -> str:
    fwd = request.headers.get("x-forwarded-for")
    if fwd:
        return fwd.split(",")[0].strip()
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()
    return request.client.host if request.client else "نامشخص"


async def load_state():
    try:
        if DATA_FILE.exists():
            async with aiofiles.open(DATA_FILE, "r", encoding="utf-8") as f:
                raw = await f.read()
            data = json.loads(raw)
            LINKS.update(data.get("links", {}))
            SUBS.update(data.get("subs", {}))
            if "password_hash" in data:
                AUTH["password_hash"] = data["password_hash"]
            if "api_key" in data:
                CONFIG["api_key"] = data["api_key"]
            if "login_path" in data:
                CONFIG["login_path"] = data["login_path"]
                AUTH["password_hash"] = data["password_hash"]
            logger.info(f"State loaded: {len(LINKS)} links, {len(SUBS)} subs")
    except Exception as e:
        logger.warning(f"Could not load state: {e}")


async def save_state():
    async with SAVE_LOCK:
        try:
            data = {
                "links": dict(LINKS),
                "subs": dict(SUBS),
                "password_hash": AUTH["password_hash"],
                "saved_at": now_iso(),
                "login_path": CONFIG.get("login_path", "/login"),
                "api_key": CONFIG["api_key"],
            }
            tmp = DATA_FILE.with_suffix(".tmp")
            async with aiofiles.open(tmp, "w", encoding="utf-8") as f:
                await f.write(json.dumps(data, ensure_ascii=False, indent=2))
            tmp.replace(DATA_FILE)
        except Exception as e:
            logger.warning(f"Could not save state: {e}")


_default_link_created = False


async def ensure_default_link():
    global _default_link_created
    if _default_link_created:
        return
    async with LINKS_LOCK:
        if not any(l.get("is_default") for l in LINKS.values()):
            uid = hashlib.sha256(f"default{CONFIG['secret']}".encode()).hexdigest()
            uid = f"{uid[:8]}-{uid[8:12]}-{uid[12:16]}-{uid[16:20]}-{uid[20:32]}"
            if uid not in LINKS:
                LINKS[uid] = {
                    "label": "لینک پیش‌فرض",
                    "limit_bytes": 0,
                    "used_bytes": 0,
                    "created_at": now_iso(),
                    "active": True,
                    "expires_at": None,
                    "note": "",
                    "is_default": True,
                    "sub_id": None,
                    "protocol": DEFAULT_PROTOCOL,
                    "fingerprint": DEFAULT_FINGERPRINT,
                    "alpn": "",
                    "port": DEFAULT_PORT,
                    "ip_limit": 0,
                    "speed_limit_bytes": DEFAULT_SPEED_LIMIT,
                    "secret": uid.replace("-", ""),
                    "path_slug": uid,
                }
                asyncio.create_task(save_state())
        _default_link_created = True


async def make_link(label="لینک جدید", limit_bytes=0, expires_at=None, note="", sub_id=None,
                    protocol=DEFAULT_PROTOCOL, fingerprint=DEFAULT_FINGERPRINT, alpn="",
                    port=DEFAULT_PORT, ip_limit=0, speed_limit_bytes=0, path_slug=None):
    if protocol not in PROTOCOLS:
        protocol = DEFAULT_PROTOCOL
    fingerprint = (fingerprint or DEFAULT_FINGERPRINT).strip().lower()
    if fingerprint not in FINGERPRINTS:
        fingerprint = DEFAULT_FINGERPRINT
    if not (MIN_PORT <= port <= MAX_PORT):
        port = DEFAULT_PORT
    uid = generate_uuid()
    path_slug = sanitize_path_slug(path_slug, uid)
    async with LINKS_LOCK:
        if not is_path_slug_available(path_slug):
            path_slug = uid
        LINKS[uid] = {
            "label": (label or "لینک جدید").strip()[:60] or "لینک جدید",
            "limit_bytes": max(0, limit_bytes),
            "used_bytes": 0,
            "created_at": now_iso(),
            "active": True,
            "expires_at": expires_at,
            "note": (note or "").strip()[:200],
            "is_default": False,
            "sub_id": sub_id,
            "protocol": protocol,
            "fingerprint": fingerprint,
            "alpn": (alpn or "").strip()[:100],
            "port": port,
            "ip_limit": max(0, ip_limit),
            "speed_limit_bytes": max(0, speed_limit_bytes),
            "secret": uid.replace("-", ""),
            "path_slug": path_slug,
        }
    if sub_id:
        async with SUBS_LOCK:
            if sub_id in SUBS:
                ids = SUBS[sub_id].setdefault("link_ids", [])
                if uid not in ids:
                    ids.append(uid)
    asyncio.create_task(save_state())
    log_activity("link", f"کانفیگ «{LINKS[uid]['label']}» ساخته شد", "ok")
    return uid, LINKS[uid]


async def remove_link(uid: str) -> str | None:
    async with LINKS_LOCK:
        if uid not in LINKS:
            return None
        label = LINKS[uid].get("label", uid)
        sub_id = LINKS[uid].get("sub_id")
        del LINKS[uid]
    if sub_id:
        async with SUBS_LOCK:
            if sub_id in SUBS:
                ids = SUBS[sub_id].get("link_ids", [])
                if uid in ids:
                    ids.remove(uid)
    asyncio.create_task(save_state())
    log_activity("link", f"کانفیگ «{label}» حذف شد", "err")
    return label


async def set_link_active(uid: str, active: bool) -> dict | None:
    async with LINKS_LOCK:
        if uid not in LINKS:
            return None
        LINKS[uid]["active"] = bool(active)
        label = LINKS[uid]["label"]
    log_activity("link", f"کانفیگ «{label}» {'فعال' if active else 'غیرفعال'} شد", "ok" if active else "warn")
    asyncio.create_task(save_state())
    return LINKS[uid]


async def create_sub_group(name="گروه جدید", desc="", password="") -> tuple[str, dict]:
    name = (name or "گروه جدید").strip()[:60]
    desc = (desc or "").strip()[:200]
    password = (password or "").strip()
    sub_id = generate_uuid()
    uuid_key = secrets.token_urlsafe(16)
    async with SUBS_LOCK:
        SUBS[sub_id] = {
            "name": name,
            "desc": desc,
            "password_hash": hash_password(password) if password else None,
            "uuid_key": uuid_key,
            "created_at": now_iso(),
            "link_ids": [],
        }
    asyncio.create_task(save_state())
    log_activity("sub", f"گروه «{name}» ساخته شد", "ok")
    return sub_id, SUBS[sub_id]


async def set_link_sub(uid: str, sub_id: str | None) -> bool:
    async with LINKS_LOCK:
        if uid not in LINKS:
            return False
        old_sub = LINKS[uid].get("sub_id")
        label = LINKS[uid].get("label", uid)
    if sub_id is not None:
        async with SUBS_LOCK:
            if sub_id not in SUBS:
                return False
    async with SUBS_LOCK:
        if old_sub and old_sub in SUBS:
            ids = SUBS[old_sub].get("link_ids", [])
            if uid in ids:
                ids.remove(uid)
        if sub_id and sub_id in SUBS:
            ids = SUBS[sub_id].setdefault("link_ids", [])
            if uid not in ids:
                ids.append(uid)
    async with LINKS_LOCK:
        if uid in LINKS:
            LINKS[uid]["sub_id"] = sub_id
    asyncio.create_task(save_state())
    log_activity("link", f"کانفیگ «{label}» {'به گروه اضافه شد' if sub_id else 'از گروه خارج شد'}", "info")
    return True


async def remove_sub_group(sub_id: str) -> str | None:
    async with SUBS_LOCK:
        if sub_id not in SUBS:
            return None
        name = SUBS[sub_id].get("name", sub_id)
        del SUBS[sub_id]
    async with LINKS_LOCK:
        for link in LINKS.values():
            if link.get("sub_id") == sub_id:
                link["sub_id"] = None
    asyncio.create_task(save_state())
    log_activity("sub", f"گروه «{name}» حذف شد", "warn")
    return name
