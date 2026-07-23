# main.py — OXNET v2.0
import asyncio
import time
from datetime import timedelta
import base64

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import Response, HTMLResponse, JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import httpx

from state import *
import state

from relay_ws import websocket_tunnel
from xhttp_oxnet import router as xhttp_router

app = FastAPI(title="OXNET", docs_url=None, redoc_url=None)

# CORS FIX: credentials + wildcard origin is invalid per the CORS spec and is
# ignored by browsers. The admin API is same-origin (dashboard), so we do not
# need credentialed cross-origin access. Public endpoints stay open without
# credentials.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Auth ─────────────────────────────────────────────────
async def create_session() -> str:
    token = secrets.token_urlsafe(32)
    async with SESSIONS_LOCK:
        SESSIONS[token] = time.time() + SESSION_TTL
    return token


async def is_valid_session(token: str | None) -> bool:
    if not token:
        return False
    async with SESSIONS_LOCK:
        exp = SESSIONS.get(token)
        if exp is None:
            return False
        if exp < time.time():
            SESSIONS.pop(token, None)
            return False
        return True


async def destroy_session(token: str | None):
    if not token:
        return
    async with SESSIONS_LOCK:
        SESSIONS.pop(token, None)


async def require_auth(request: Request):
    api_key = request.headers.get("X-API-Key")
    if api_key and api_key == state.CONFIG.get("api_key"):
        return "api_key"
    token = request.cookies.get(SESSION_COOKIE)
    if not await is_valid_session(token):
        raise HTTPException(status_code=401, detail="unauthorized")
    return token


# ── Startup / Shutdown ──────────────────────────────────────
@app.on_event("startup")
async def startup():
    limits = httpx.Limits(max_connections=500, max_keepalive_connections=100)
    timeout = httpx.Timeout(30.0, connect=10.0)
    state.http_client = httpx.AsyncClient(limits=limits, timeout=timeout, follow_redirects=True)
    await load_state()
    log_activity("system", "سرور راه‌اندازی شد", "ok")
    logger.info(f"OXNET v{PANEL_VERSION} started on port {CONFIG['port']}")


@app.on_event("shutdown")
async def shutdown():
    await save_state()
    if state.http_client:
        await state.http_client.aclose()


# ── Basic endpoints ──────────────────────────────────────
@app.get("/")
async def root():
    return {"service": "OXNET", "version": PANEL_VERSION, "status": "active"}


@app.get("/health")
async def health():
    return {"status": "ok", "connections": len(connections), "uptime": uptime()}


# ── Subscription (single link) ────────────────────────────────

@app.get("/sub/{uuid}")
async def subscription_single(uuid: str, request: Request):
    from urllib.parse import quote
    import base64
    async with LINKS_LOCK:
        real_uid, link = resolve_link_key(uuid)
    if not real_uid or not link or not is_link_allowed(link):
        raise HTTPException(status_code=404, detail="not found or inactive")
    host = get_host(request)
    sub_text = subscription_text_for_link(link, real_uid, host)
    
    user_agent = request.headers.get("user-agent", "").lower()
    title = quote(link["label"])
    
    if "clash" in user_agent or "meta" in user_agent:
        lines = sub_text.split("
")
        proxies = []
        names = []
        for line in lines:
            if line.startswith("vless://"):
                parts = line.split("vless://")[1].split("@")
                uid = parts[0]
                rest = parts[1].split(":")
                srv = rest[0]
                port_params = rest[1].split("?")
                prt = port_params[0]
                name = port_params[1].split("#")[1] if "#" in port_params[1] else "VLESS"
                proxies.append("  - name: '" + name + "'
    type: vless
    server: " + srv + "
    port: " + prt + "
    uuid: " + uid + "
    udp: true
    tls: true
    network: ws
    servername: " + srv + "
    ws-opts:
      path: /ws
      headers:
        Host: " + srv)
                names.append("      - '" + name + "'")
        yaml_data = "port: 7890
socks-port: 7891
allow-lan: true
mode: rule
log-level: info
proxies:
" + "
".join(proxies) + "
proxy-groups:
  - name: PROXY
    type: select
    proxies:
" + "
".join(names) + "
rules:
  - DOMAIN-SUFFIX,ir,DIRECT
  - GEOIP,IR,DIRECT
  - MATCH,PROXY
"
        return Response(content=yaml_data, media_type="text/yaml", headers={"profile-title": title})
        
    content = base64.b64encode(sub_text.encode()).decode()
    return Response(content=content, media_type="text/plain", headers={"profile-title": title})



@app.get("/sub-all")
async def subscription_all(request: Request, _=Depends(require_auth)):
    host = get_host(request)
    async with LINKS_LOCK:
        lines = []
        for uid, d in LINKS.items():
            if is_link_allowed(d):
                lines.extend(links_for_link(d, uid, host))
    content = base64.b64encode("\n".join(lines).encode()).decode()
    return Response(content=content, media_type="text/plain")


# ── State export / import (NEW) ────────────────────────────────
@app.get("/api/export")
async def export_state(_=Depends(require_auth)):
    async with LINKS_LOCK:
        l = dict(LINKS)
    async with SUBS_LOCK:
        s = dict(SUBS)
    return {"links": l, "subs": s, "exported_at": now_iso(), "version": PANEL_VERSION}


@app.post("/api/import")
async def import_state(request: Request, _=Depends(require_auth)):
    body = await request.json()
    imported = 0
    async with LINKS_LOCK:
        for uid, link in (body.get("links") or {}).items():
            if uid not in LINKS and isinstance(link, dict):
                LINKS[uid] = link
                imported += 1
    async with SUBS_LOCK:
        for sid, sub in (body.get("subs") or {}).items():
            if sid not in SUBS and isinstance(sub, dict):
                SUBS[sid] = sub
    await save_state()
    log_activity("system", f"{imported} کانفیگ ایمپورت شد", "ok")
    return {"ok": True, "imported": imported}



@app.get("/api/sys-settings")
async def get_sys_settings(_=Depends(require_auth)):
    return {"login_path": state.CONFIG.get("login_path", "/login"), "api_key": state.CONFIG.get("api_key", "")}

@app.post("/api/sys-settings")
async def update_sys_settings(request: Request, _=Depends(require_auth)):
    body = await request.json()
    new_path = body.get("login_path", "/login").strip()
    if not new_path.startswith("/"):
        new_path = "/" + new_path
    state.CONFIG["login_path"] = new_path
    state.CONFIG["api_key"] = body.get("api_key", "").strip()
    await save_state()
    return {"ok": True}

@app.get("/api/protocols")
async def list_protocols(_=Depends(require_auth)):
    return {"protocols": list(PROTOCOLS), "default": DEFAULT_PROTOCOL, "fingerprints": list(FINGERPRINTS)}


# ════════════════════════════════════════════════════════════════════════════
# SUB GROUP endpoints
# ════════════════════════════════════════════════════════════════════════════
@app.post("/api/subs")
async def create_sub(request: Request, _=Depends(require_auth)):
    body = await request.json()
    name = (body.get("name") or "گروه جدید").strip()[:60]
    desc = (body.get("desc") or "").strip()[:200]
    password = (body.get("password") or "").strip()
    sub_id, sub_data = await create_sub_group(name, desc, password)
    host = get_host(request)
    return {
        "sub_id": sub_id,
        **sub_data,
        "public_url": f"https://{host}/p/{sub_data['uuid_key']}",
        "sub_url": f"https://{host}/sub-group/{sub_data['uuid_key']}",
    }


@app.get("/api/subs")
async def list_subs(request: Request, _=Depends(require_auth)):
    host = get_host(request)
    async with SUBS_LOCK:
        snap_subs = dict(SUBS)
    async with LINKS_LOCK:
        snap_links = dict(LINKS)
    result = []
    for sid, s in snap_subs.items():
        link_ids = s.get("link_ids", [])
        active_count = sum(1 for lid in link_ids if is_link_allowed(snap_links.get(lid)))
        total_used = sum(snap_links[lid].get("used_bytes", 0) for lid in link_ids if lid in snap_links)
        result.append({
            "sub_id": sid,
            **s,
            "password_hash": None,
            "has_password": s.get("password_hash") is not None,
            "links_count": len(link_ids),
            "active_count": active_count,
            "total_used_bytes": total_used,
            "total_used_fmt": fmt_bytes(total_used),
            "public_url": f"https://{host}/p/{s['uuid_key']}",
            "sub_url": f"https://{host}/sub-group/{s['uuid_key']}",
        })
    result.sort(key=lambda x: x["created_at"], reverse=True)
    return {"subs": result}


@app.patch("/api/subs/{sub_id}")
async def update_sub(sub_id: str, request: Request, _=Depends(require_auth)):
    body = await request.json()
    async with SUBS_LOCK:
        if sub_id not in SUBS:
            raise HTTPException(status_code=404, detail="sub not found")
        s = SUBS[sub_id]
        if "name" in body:
            s["name"] = str(body["name"])[:60]
        if "desc" in body:
            s["desc"] = str(body["desc"])[:200]
        if "password" in body:
            pw = str(body["password"]).strip()
            s["password_hash"] = hash_password(pw) if pw else None
        if "link_ids" in body:
            s["link_ids"] = list(body["link_ids"])
    asyncio.create_task(save_state())
    return {"ok": True}


@app.delete("/api/subs/{sub_id}")
async def delete_sub(sub_id: str, _=Depends(require_auth)):
    name = await remove_sub_group(sub_id)
    if name is None:
        raise HTTPException(status_code=404, detail="sub not found")
    return {"ok": True, "deleted": sub_id}


@app.post("/api/subs/{sub_id}/links")
async def assign_link_to_sub(sub_id: str, request: Request, _=Depends(require_auth)):
    body = await request.json()
    link_id = str(body.get("link_id", ""))
    action = str(body.get("action", "add"))
    if action == "add":
        ok = await set_link_sub(link_id, sub_id)
    else:
        ok = await set_link_sub(link_id, None)
    if not ok:
        raise HTTPException(status_code=404, detail="link or sub not found")
    return {"ok": True}


# ── Public sub-group subscription file ────────────────────────────
@app.get("/sub-group/{uuid_key}")
async def sub_group_subscription(uuid_key: str, request: Request):
    from urllib.parse import quote
    async with SUBS_LOCK:
        sub = next((s for s in SUBS.values() if s.get("uuid_key") == uuid_key), None)
    if not sub:
        raise HTTPException(status_code=404, detail="not found")

    if sub.get("password_hash"):
        pw = request.query_params.get("pw", "")
        if hash_password(pw) != sub["password_hash"]:
            raise HTTPException(status_code=403, detail="wrong password")

    host = get_host(request)
    link_ids = sub.get("link_ids", [])
    async with LINKS_LOCK:
        lines = []
        for lid in link_ids:
            link = LINKS.get(lid)
            if link and is_link_allowed(link):
                lines.extend(links_for_link(link, lid, host))

    content = base64.b64encode("\n".join(lines).encode()).decode()
    return Response(
        content=content,
        media_type="text/plain",
        headers={"profile-title": quote(sub["name"]), "profile-update-interval": "12"},
    )


# ── Auth endpoints ──────────────────────────────────────────
@app.post("/api/login")
async def api_login(request: Request):
    body = await request.json()
    ip = client_ip(request)
    if hash_password(str(body.get("password", ""))) != AUTH["password_hash"]:
        log_activity("auth", f"تلاش ورود ناموفق از {ip}", "err")
        raise HTTPException(status_code=401, detail="رمز عبور اشتباه است")
    token = await create_session()
    log_activity("auth", f"ورود موفق به پنل از {ip}", "ok")
    resp = JSONResponse({"ok": True})
    resp.set_cookie(SESSION_COOKIE, token, max_age=SESSION_TTL, httponly=True, samesite="lax", path="/")
    return resp


@app.post("/api/logout")
async def api_logout(request: Request):
    await destroy_session(request.cookies.get(SESSION_COOKIE))
    resp = JSONResponse({"ok": True})
    resp.delete_cookie(SESSION_COOKIE, path="/")
    return resp


@app.get("/api/me")
async def api_me(request: Request):
    return {"authenticated": await is_valid_session(request.cookies.get(SESSION_COOKIE))}


@app.post("/api/change-password")
async def api_change_password(request: Request, token=Depends(require_auth)):
    body = await request.json()
    current = str(body.get("current_password", body.get("old_password", "")))
    if hash_password(current) != AUTH["password_hash"]:
        raise HTTPException(status_code=400, detail="رمز فعلی اشتباه است")
    new = str(body.get("new_password", ""))
    if len(new) < 4:
        raise HTTPException(status_code=400, detail="رمز جدید باید حداقل ۴ کاراکتر باشد")
    AUTH["password_hash"] = hash_password(new)
    async with SESSIONS_LOCK:
        SESSIONS.clear()
        SESSIONS[token] = time.time() + SESSION_TTL
    await save_state()
    log_activity("auth", "رمز عبور پنل تغییر کرد", "ok")
    return {"ok": True}


# ── Stats ────────────────────────────────────────────────

def get_sys_info():
    import os
    cpu = 0
    mem_percent = 0
    mem_used = 0
    mem_total = 0
    try:
        with open('/proc/stat', 'r') as f:
            lines = f.readlines()
            cpu_times = list(map(int, lines[0].split()[1:]))
            idle = cpu_times[3] + cpu_times[4]
            total = sum(cpu_times)
            cpu = round(100.0 * (1.0 - idle / total), 1) if total > 0 else 0
    except: pass
    try:
        with open('/proc/meminfo', 'r') as f:
            mem_data = {}
            for line in f:
                parts = line.split()
                mem_data[parts[0]] = int(parts[1])
            total = mem_data.get('MemTotal:', 0)
            free = mem_data.get('MemAvailable:', mem_data.get('MemFree:', 0))
            if total > 0:
                mem_percent = round(100.0 * (1.0 - free / total), 1)
                mem_total = round(total / (1024*1024), 2)
                mem_used = round((total - free) / (1024*1024), 2)
    except: pass
    try:
        import shutil
        disk = shutil.disk_usage('/')
        disk_percent = round(disk.used / disk.total * 100, 1)
    except:
        disk_percent = 0
    return cpu, mem_percent, mem_used, mem_total, disk_percent

@app.get("/stats")
async def get_stats(_=Depends(require_auth)):
    async with LINKS_LOCK:
        snap = dict(LINKS)
    
    cpu, mem_percent, mem_used, mem_total, disk_percent = get_sys_info()
    
    return {
        "active_connections": len(connections),
        "total_traffic_mb": round(stats["total_bytes"] / (1024 ** 2), 2),
        "total_requests": stats["total_requests"],
        "total_errors": stats["total_errors"],
        "uptime": uptime(),
        "timestamp": now_iso(),
        "hourly": dict(hourly_traffic),
        "recent_errors": list(error_logs)[-10:],
        "links_count": len(snap),
        "active_links": sum(1 for l in snap.values() if is_link_allowed(l)),
        "expired_links": sum(1 for l in snap.values() if is_link_expired(l)),
        "subs_count": len(SUBS),
        "sys_cpu": cpu,
        "sys_mem_percent": mem_percent,
        "sys_mem_used_gb": mem_used,
        "sys_mem_total_gb": mem_total,
        "sys_disk_percent": disk_percent
    }



@app.get("/api/activity")
async def get_activity(_=Depends(require_auth)):
    return {"logs": list(activity_logs)[-150:]}


@app.get("/api/connections")
async def get_connections(_=Depends(require_auth)):
    async with LINKS_LOCK:
        snap = dict(LINKS)
    grouped: dict[str, dict] = {}
    for conn_id, c in connections.items():
        ip = c.get("ip", "نامشخص")
        link = snap.get(c.get("uuid"))
        label = link.get("label") if link else "نامشخص"
        g = grouped.get(ip)
        if g is None:
            g = {"ip": ip, "sessions": 0, "bytes": 0, "labels": set(), "transports": set(),
                 "first_connected_at": c.get("connected_at"), "last_connected_at": c.get("connected_at")}
            grouped[ip] = g
        g["sessions"] += 1
        g["bytes"] += c.get("bytes", 0)
        g["labels"].add(label)
        g["transports"].add(c.get("transport", "ws"))
        ca = c.get("connected_at")
        if ca:
            if not g["first_connected_at"] or ca < g["first_connected_at"]:
                g["first_connected_at"] = ca
            if not g["last_connected_at"] or ca > g["last_connected_at"]:
                g["last_connected_at"] = ca
    result = []
    for ip, g in grouped.items():
        result.append({
            "ip": ip,
            "sessions": g["sessions"],
            "labels": sorted(g["labels"]),
            "label": " · ".join(sorted(g["labels"])) if g["labels"] else "نامشخص",
            "transports": sorted(g["transports"]),
            "bytes": g["bytes"],
            "bytes_fmt": fmt_bytes(g["bytes"]),
            "connected_at": g["first_connected_at"],
            "last_connected_at": g["last_connected_at"],
        })
    result.sort(key=lambda x: x.get("last_connected_at") or "", reverse=True)
    return {"connections": result, "count": len(result), "raw_count": len(connections)}


# ── Link Management ─────────────────────────────────────────
@app.post("/api/links")
async def create_link(request: Request, _=Depends(require_auth)):
    body = await request.json()
    lv = float(body.get("limit_value") or 0)
    lu = body.get("limit_unit") or "GB"
    limit_bytes = 0 if lv <= 0 else parse_size_to_bytes(lv, lu)
    exp_days = int(body.get("expires_days") or 0)
    expires_at = (now_ir() + timedelta(days=exp_days)).isoformat() if exp_days > 0 else None
    try:
        port = int(body.get("port") or DEFAULT_PORT)
    except (TypeError, ValueError):
        port = DEFAULT_PORT
    try:
        ip_limit = int(body.get("ip_limit") or 0)
    except (TypeError, ValueError):
        ip_limit = 0
    sv = float(body.get("speed_limit_value") or 0)
    su = body.get("speed_limit_unit") or "MBIT"
    speed_limit_bytes = 0 if sv <= 0 else parse_speed_to_bytes(sv, su)

    uid, link = await make_link(
        label=body.get("label") or "لینک جدید",
        limit_bytes=limit_bytes,
        expires_at=expires_at,
        note=body.get("note") or "",
        sub_id=body.get("sub_id") or None,
        protocol=body.get("protocol") or DEFAULT_PROTOCOL,
        fingerprint=body.get("fingerprint") or DEFAULT_FINGERPRINT,
        alpn=body.get("alpn") or "",
        port=port,
        ip_limit=ip_limit,
        speed_limit_bytes=speed_limit_bytes,
        path_slug=body.get("path_slug") or body.get("path") or None,
    )
    host = get_host(request)
    return {
        "uuid": uid,
        **link,
        "expired": False,
        "vless_link": primary_link_for_link(link, uid, host),
        "links": links_for_link(link, uid, host),
        "path_slug": link.get("path_slug", uid),
        "sub_url": f"https://{host}/sub/{uid}",
    }


@app.get("/api/links")
async def list_links(request: Request, _=Depends(require_auth)):
    host = get_host(request)
    async with LINKS_LOCK:
        snap = dict(LINKS)
    result = []
    for uid, d in snap.items():
        proto = d.get("protocol", DEFAULT_PROTOCOL)
        result.append({
            "uuid": uid,
            **d,
            "protocol": proto,
            "expired": is_link_expired(d),
            "vless_link": primary_link_for_link(d, uid, host),
            "links": links_for_link(d, uid, host),
            "path_slug": d.get("path_slug", uid),
            "sub_url": f"https://{host}/sub/{uid}",
            "connected_ips": len(unique_ips_for_uuid(uid)),
        })
    result.sort(key=lambda x: x["created_at"], reverse=True)
    return {"links": result}


@app.patch("/api/links/{uid}")
async def update_link(uid: str, request: Request, _=Depends(require_auth)):
    body = await request.json()
    async with LINKS_LOCK:
        if uid not in LINKS:
            raise HTTPException(status_code=404, detail="link not found")
        link = LINKS[uid]
        old_sub = link.get("sub_id")
        label = link.get("label")
        if "active" in body:
            link["active"] = bool(body["active"])
            log_activity("link", f"کانفیگ «{label}» {'فعال' if link['active'] else 'غیرفعال'} شد", "ok" if link["active"] else "warn")
        if "label" in body:
            link["label"] = str(body["label"])[:60]
        if "note" in body:
            link["note"] = str(body["note"])[:200]
        if "reset_usage" in body and body["reset_usage"]:
            link["used_bytes"] = 0
            log_activity("link", f"مصرف کانفیگ «{label}» ریست شد", "info")
        if "limit_value" in body:
            lv = float(body.get("limit_value") or 0)
            lu = body.get("limit_unit") or "GB"
            link["limit_bytes"] = 0 if lv <= 0 else parse_size_to_bytes(lv, lu)
        if "expires_days" in body:
            ed = int(body["expires_days"] or 0)
            link["expires_at"] = (now_ir() + timedelta(days=ed)).isoformat() if ed > 0 else None
        if "protocol" in body:
            proto = str(body.get("protocol") or DEFAULT_PROTOCOL).strip()
            link["protocol"] = proto if proto in PROTOCOLS else DEFAULT_PROTOCOL
        if "path_slug" in body or "path" in body:
            wanted = body.get("path_slug", body.get("path"))
            slug = sanitize_path_slug(str(wanted or ""), uid)
            if not is_path_slug_available(slug, uid):
                raise HTTPException(status_code=409, detail="path already exists")
            link["path_slug"] = slug
        if "fingerprint" in body:
            fp = str(body.get("fingerprint") or DEFAULT_FINGERPRINT).strip().lower()
            link["fingerprint"] = fp if fp in FINGERPRINTS else DEFAULT_FINGERPRINT
        if "alpn" in body:
            link["alpn"] = str(body.get("alpn") or "").strip()[:100]
        if "port" in body:
            try:
                p = int(body.get("port") or DEFAULT_PORT)
            except (TypeError, ValueError):
                p = DEFAULT_PORT
            link["port"] = p if (MIN_PORT <= p <= MAX_PORT) else DEFAULT_PORT
        if "ip_limit" in body:
            try:
                il = int(body.get("ip_limit") or 0)
            except (TypeError, ValueError):
                il = 0
            link["ip_limit"] = max(0, il)
        if "speed_limit_value" in body:
            sv = float(body.get("speed_limit_value") or 0)
            su = body.get("speed_limit_unit") or "MBIT"
            link["speed_limit_bytes"] = 0 if sv <= 0 else parse_speed_to_bytes(sv, su)
            try:
                from speed_limit import reset_bucket
                reset_bucket(uid)
            except ImportError:
                pass
        if any(k in body for k in ("label", "note", "limit_value", "expires_days", "fingerprint", "alpn", "port", "ip_limit", "speed_limit_value")):
            log_activity("link", f"کانفیگ «{link['label']}» ویرایش شد", "info")
        new_sub = body.get("sub_id", "UNCHANGED")
        if new_sub != "UNCHANGED":
            link["sub_id"] = new_sub or None

    if new_sub != "UNCHANGED":
        async with SUBS_LOCK:
            if old_sub and old_sub in SUBS:
                ids = SUBS[old_sub].get("link_ids", [])
                if uid in ids:
                    ids.remove(uid)
            if new_sub and new_sub in SUBS:
                ids = SUBS[new_sub].setdefault("link_ids", [])
                if uid not in ids:
                    ids.append(uid)

    asyncio.create_task(save_state())
    return {"ok": True}


@app.delete("/api/links/{uid}")
async def delete_link(uid: str, _=Depends(require_auth)):
    label = await remove_link(uid)
    if label is None:
        raise HTTPException(status_code=404, detail="link not found")
    return {"ok": True, "deleted": uid}


# ══ VLESS / Trojan Relay (WebSocket) ══════════════════════════
app.add_api_websocket_route("/ws/{path_key}", websocket_tunnel)

# ══ XHTTP ═══════════════════════════════════════════
app.include_router(xhttp_router)

# ── HTTP Proxy ───────────────────────────────────────────
_HOP = {"connection", "keep-alive", "proxy-authenticate", "proxy-authorization",
        "te", "trailers", "transfer-encoding", "upgrade", "content-encoding", "content-length"}


@app.api_route("/proxy/{target_url:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
async def http_proxy(target_url: str, request: Request):
    if not target_url.startswith("http"):
        target_url = "https://" + target_url
    try:
        body = await request.body()
        headers = {k: v for k, v in request.headers.items() if k.lower() not in _HOP and k.lower() != "host"}
        resp = await state.http_client.request(method=request.method, url=target_url, headers=headers, content=body)
        stats["total_bytes"] += len(resp.content)
        stats["total_requests"] += 1
        hourly_traffic[now_ir().strftime("%H:00")] += len(resp.content)
        return Response(content=resp.content, status_code=resp.status_code,
                        headers={k: v for k, v in resp.headers.items() if k.lower() not in _HOP})
    except Exception as exc:
        stats["total_errors"] += 1
        error_logs.append({"error": str(exc), "url": target_url, "time": now_iso()})
        raise HTTPException(status_code=502, detail=f"Proxy error: {exc}")


# ── Public sub page ───────────────────────────────────────
@app.get("/p/{uuid_key}", response_class=HTMLResponse)
async def public_sub_page(uuid_key: str, request: Request):
    try:
        from pages import get_public_page_html
    except ImportError:
        return HTMLResponse("Pages module missing", status_code=500)
    async with SUBS_LOCK:
        sub = next(({"sub_id": sid, **s} for sid, s in SUBS.items() if s.get("uuid_key") == uuid_key), None)
    if not sub:
        return HTMLResponse("<h2 style='font-family:sans-serif;padding:40px'>گروه پیدا نشد</h2>", status_code=404)
    return HTMLResponse(content=get_public_page_html(uuid_key))


@app.get("/api/public/sub/{uuid_key}")
async def public_sub_data(uuid_key: str, request: Request):
    async with SUBS_LOCK:
        sub_entry = next(((sid, s) for sid, s in SUBS.items() if s.get("uuid_key") == uuid_key), None)
    if not sub_entry:
        raise HTTPException(status_code=404, detail="not found")
    sub_id, sub = sub_entry

    has_pw = sub.get("password_hash") is not None
    if has_pw:
        pw = request.query_params.get("pw", "")
        if hash_password(pw) != sub["password_hash"]:
            return JSONResponse({"locked": True, "name": sub["name"]})

    host = get_host(request)
    link_ids = sub.get("link_ids", [])
    async with LINKS_LOCK:
        snap = dict(LINKS)

    links_out = []
    active_conns = 0
    for lid in link_ids:
        link = snap.get(lid)
        if not link:
            continue
        allowed = is_link_allowed(link)
        conn_count = sum(1 for c in connections.values() if c.get("uuid") == lid)
        active_conns += conn_count
        proto = link.get("protocol", DEFAULT_PROTOCOL)
        links_out.append({
            "uuid": lid,
            "label": link["label"],
            "active": allowed,
            "protocol": proto,
            "used_bytes": link.get("used_bytes", 0),
            "used_fmt": fmt_bytes(link.get("used_bytes", 0)),
            "limit_bytes": link.get("limit_bytes", 0),
            "limit_fmt": "∞" if link.get("limit_bytes", 0) == 0 else fmt_bytes(link["limit_bytes"]),
            "expires_at": link.get("expires_at"),
            "vless_link": primary_link_for_link(link, lid, host),
            "links": links_for_link(link, lid, host),
            "sub_url": f"https://{host}/sub/{lid}",
            "connections": conn_count,
            "ip_limit": link.get("ip_limit", 0),
            "speed_limit_bytes": link.get("speed_limit_bytes", 0),
        })

    total_used = sum(l["used_bytes"] for l in links_out)
    return {
        "locked": False,
        "name": sub["name"],
        "desc": sub.get("desc", ""),
        "sub_url": f"https://{host}/sub-group/{uuid_key}",
        "active_connections": active_conns,
        "total_used_fmt": fmt_bytes(total_used),
        "links": links_out,
    }


# ── HTML Pages (login + dashboard) ──────────────────────────────



@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    if not await is_valid_session(request.cookies.get(SESSION_COOKIE)):
        return RedirectResponse(url="/login")
    await ensure_default_link()
    try:
        from pages import DASHBOARD_HTML
        return HTMLResponse(content=DASHBOARD_HTML)
    except ImportError:
        return HTMLResponse("Pages module missing", status_code=500)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=CONFIG["port"], log_level="info", workers=1)

# ── Fallback (Camouflage) ──────────────────────────────


@app.get("/{path:path}", response_class=HTMLResponse)
async def catch_all(path: str, request: Request):
    target_path = "/" + path
    if target_path == state.CONFIG.get("login_path", "/login"):
        if await is_valid_session(request.cookies.get(SESSION_COOKIE)):
            return RedirectResponse(url="/dashboard")
        try:
            from pages import LOGIN_HTML
            return HTMLResponse(content=LOGIN_HTML)
        except ImportError:
            return HTMLResponse("Pages module missing", status_code=500)
    # Camouflage fallback for unknown paths
    return RedirectResponse(url="https://www.apple.com")

# ── UVLoop integration ─────────────────────────────────
if __name__ == "__main__":
    
    uvicorn.run("main:app", host="0.0.0.0", port=CONFIG["port"], log_level="info", workers=1)
