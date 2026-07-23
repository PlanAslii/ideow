# pages.py — OXNET v2.0
# Redesigned: Clean Minimalist Light/Dark Theme (No Neon, No Glow)
# A professional, Apple/Vercel inspired interface with flat colors.

_BASE_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;500;600;700;800&display=swap');
:root {
  --bg: #f8fafc;
  --bg-card: #ffffff;
  --text-main: #0f172a;
  --text-muted: #64748b;
  --border: #e2e8f0;
  --border-hover: #cbd5e1;
  --primary: #0f172a;
  --primary-hover: #334155;
  --danger: #ef4444;
  --success: #10b981;
  --warn: #f59e0b;
  --radius: 12px;
  --shadow: 0 1px 3px rgba(0,0,0,0.05), 0 4px 12px rgba(0,0,0,0.03);
}
[data-theme="dark"] {
  --bg: #09090b;
  --bg-card: #141416;
  --text-main: #f4f4f5;
  --text-muted: #a1a1aa;
  --border: #27272a;
  --border-hover: #3f3f46;
  --primary: #ffffff;
  --primary-hover: #e4e4e7;
  --danger: #f87171;
  --shadow: 0 4px 12px rgba(0,0,0,0.4);
}
* { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
html, body { margin: 0; padding: 0; }
body {
  font-family: 'Vazirmatn', system-ui, sans-serif;
  background-color: var(--bg); color: var(--text-main); direction: rtl; min-height: 100vh;
  transition: background-color 0.2s ease, color 0.2s ease; letter-spacing: 0.1px;
}
.btn {
  cursor: pointer; border: 1px solid transparent; border-radius: 8px; padding: 10px 16px;
  font-family: inherit; font-size: 14px; font-weight: 600;
  background: var(--primary); color: var(--bg); transition: all 0.2s; display: inline-flex;
  align-items: center; justify-content: center; gap: 8px;
}
[data-theme="dark"] .btn { color: #000; }
.btn:hover { background: var(--primary-hover); transform: translateY(-1px); }
.btn:active { transform: translateY(0); }
.btn.ghost { background: transparent; border-color: var(--border); color: var(--text-main); }
.btn.ghost:hover { background: var(--bg); border-color: var(--border-hover); }
.btn.danger { background: var(--danger); color: #fff; }
.btn.danger:hover { filter: brightness(1.1); }
.btn.sm { padding: 6px 12px; font-size: 12.5px; border-radius: 6px; }

.chip {
  display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px;
  border-radius: 6px; font-size: 12px; font-weight: 600; border: 1px solid var(--border);
  background: var(--bg);
}
.chip.ok { color: var(--success); border-color: rgba(16, 185, 129, 0.3); }
.chip.err { color: var(--danger); border-color: rgba(239, 68, 68, 0.3); }
.chip.warn { color: var(--warn); border-color: rgba(245, 158, 11, 0.3); }
.chip.proto { color: #3b82f6; border-color: rgba(59, 130, 246, 0.3); }

input, select, textarea {
  width: 100%; padding: 10px 14px; border-radius: 8px;
  border: 1px solid var(--border); background: var(--bg-card); color: var(--text-main);
  font-family: inherit; font-size: 14px; transition: all 0.2s;
}
input:focus, select:focus, textarea:focus {
  outline: none; border-color: var(--text-muted); box-shadow: 0 0 0 2px rgba(128,128,128,0.1);
}
label { font-size: 13px; color: var(--text-muted); margin-bottom: 6px; display: block; font-weight: 600; }
.card {
  background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius);
  box-shadow: var(--shadow); transition: border 0.2s;
}
.card:hover { border-color: var(--border-hover); }

/* Theme Toggle Button */
.theme-toggle {
  position: fixed; bottom: 20px; left: 20px; width: 44px; height: 44px;
  border-radius: 50%; background: var(--bg-card); border: 1px solid var(--border);
  display: flex; align-items: center; justify-content: center; cursor: pointer;
  box-shadow: var(--shadow); z-index: 100; font-size: 18px; color: var(--text-main);
  transition: all 0.2s;
}
.theme-toggle:hover { transform: scale(1.05); }
"""

_THEME_JS = """
<script>
function initTheme(){
  var t = localStorage.getItem('theme') || 'light';
  document.documentElement.setAttribute('data-theme', t);
}
function toggleTheme(){
  var html = document.documentElement;
  var isDark = html.getAttribute('data-theme') === 'dark';
  var newT = isDark ? 'light' : 'dark';
  html.setAttribute('data-theme', newT);
  localStorage.setItem('theme', newT);
}
initTheme();
</script>
"""

LOGIN_HTML = """<!doctype html><html lang=fa dir=rtl><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1,maximum-scale=1">
<title>OXNET • ورود</title>__THEME_JS__
<style>__CSS__
.wrap{min-height:100vh;display:flex;align-items:center;justify-content:center;padding:22px}
.login{width:100%;max-width:380px;padding:40px 32px;text-align:center;animation:fade .4s ease}
@keyframes fade{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
.logo{width:64px;height:64px;margin:0 auto 20px;border-radius:16px;background:var(--primary);display:grid;place-items:center;font-size:24px;font-weight:800;color:var(--bg)}
.login h1{margin:0 0 8px;font-size:24px;font-weight:800;color:var(--text-main)}
.login p{margin:0 0 32px;color:var(--text-muted);font-size:14px}
.field{text-align:right;margin-bottom:20px}
.err-msg{color:var(--danger);font-size:13px;min-height:20px;margin-bottom:16px;font-weight:600}
.foot{margin-top:28px;color:var(--text-muted);font-size:12px}
</style></head><body>
<button class="theme-toggle" onclick="toggleTheme()">تغییر ظاهر</button>
<div class=wrap><form class="card login" onsubmit="return doLogin(event)">
<div class=logo>OX</div><h1>OXNET</h1><p>کنترل‌پنل مدیریت شبکه</p>
<div class=err-msg id=err></div>
<div class=field><label>رمز عبور</label>
<input type=password id=pw placeholder="رمز عبور سیستم" autofocus></div>
<button class=btn style=width:100%;margin-top:8px type=submit>ورود به پنل</button>
<div class=foot>محافظت شده • OXNET Core</div>
</form></div>
<script>
async function doLogin(e){e.preventDefault();var er=document.getElementById('err');er.textContent='';
try{var r=await fetch('/api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({password:document.getElementById('pw').value})});
if(r.ok){location.href='/dashboard';}else{var d=await r.json().catch(()=>({}));er.textContent=d.detail||'رمز اشتباه است';}}catch(x){er.textContent='خطای ارتباط';}return false;}
</script></body></html>""".replace("__CSS__", _BASE_CSS).replace("__THEME_JS__", _THEME_JS)


def get_public_page_html(uuid_key: str) -> str:
    return _PUBLIC_HTML.replace("__KEY__", uuid_key).replace("__CSS__", _BASE_CSS).replace("__THEME_JS__", _THEME_JS)


_PUBLIC_HTML = """<!doctype html><html lang=fa dir=rtl><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>OXNET • اشتراک</title>__THEME_JS__
<script src="https://cdn.jsdelivr.net/npm/qrcodejs@1.0.0/qrcode.min.js"></script>
<style>__CSS__
.wrap{max-width:760px;margin:0 auto;padding:32px 16px 80px}
.head{text-align:center;padding:24px 16px}
.head .logo{width:56px;height:56px;margin:0 auto 16px;border-radius:14px;background:var(--primary);display:grid;place-items:center;font-size:22px;font-weight:800;color:var(--bg)}
.head h1{margin:0;font-size:22px;font-weight:800}.head p{color:var(--text-muted);margin:8px 0 0;font-size:14px}
.metrics{display:flex;gap:12px;justify-content:center;margin:24px 0 32px;flex-wrap:wrap}
.metric{flex:1;min-width:130px;padding:20px;text-align:center;border-radius:12px;border:1px solid var(--border);background:var(--bg-card)}
.metric b{display:block;font-size:24px;font-weight:700;color:var(--text-main)}
.metric span{color:var(--text-muted);font-size:12px;font-weight:600;margin-top:6px;display:inline-block}
.subbar{display:flex;gap:12px;margin-bottom:28px}
.item{padding:24px;margin-bottom:16px;animation:fade .3s ease}
@keyframes fade{from{opacity:0}to{opacity:1}}
.item .top{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:16px}
.item .top b{font-size:16px;font-weight:700}
.bar{height:6px;border-radius:4px;background:var(--border);overflow:hidden;margin:12px 0;box-shadow:inset 0 1px 2px rgba(0,0,0,0.05)}
.bar i{display:block;height:100%;border-radius:4px;background:var(--primary);transition:width .6s ease}
.meta{display:flex;justify-content:space-between;color:var(--text-muted);font-size:13px;font-weight:600}
.acts{display:flex;gap:10px;margin-top:20px;flex-wrap:wrap}
.locked{max-width:400px;margin:60px auto;padding:32px;text-align:center}
.modal-bg{position:fixed;inset:0;background:rgba(0,0,0,0.5);backdrop-filter:blur(4px);z-index:50;display:none;align-items:center;justify-content:center;padding:20px}
.modal-bg.show{display:flex}
.modal{max-width:440px;width:100%;padding:28px;text-align:center;background:var(--bg-card);border:1px solid var(--border);border-radius:16px;animation:fade .2s}
#qrbox{background:#fff;padding:16px;border-radius:12px;display:inline-block;margin:16px 0;border:1px solid #e2e8f0}
.linklist{text-align:right;max-height:260px;overflow:auto;margin-top:12px}
.linkrow{display:flex;gap:10px;align-items:center;background:var(--bg);border:1px solid var(--border);border-radius:8px;padding:10px 14px;margin-bottom:8px;font-size:12px;word-break:break-all}
.linkrow span{flex:1;color:var(--text-muted)}
.toast{position:fixed;bottom:24px;left:50%;transform:translateX(-50%);background:var(--primary);color:var(--bg);padding:12px 24px;border-radius:8px;font-weight:600;font-size:13px;z-index:80;opacity:0;transition:all .3s;pointer-events:none}
.toast.show{opacity:1;transform:translateX(-50%) translateY(-10px)}
</style></head><body>
<button class="theme-toggle" onclick="toggleTheme()">تغییر ظاهر</button>
<div class=wrap id=app><div style=text-align:center;padding:100px;color:var(--text-muted)>در حال دریافت…</div></div>
<div class=modal-bg id=modalBg onclick="if(event.target===this)closeModal()"><div class="modal"><h3 id=mTitle style=margin:0 0 8px;font-size:20px></h3><div id=qrbox></div><div class=linklist id=mLinks></div><button class="btn ghost" style=width:100%;margin-top:16px onclick=closeModal()>بستن</button></div></div>
<div class=toast id=toast></div>
<script>
var KEY='__KEY__',DATA=null;
function toast(m){var t=document.getElementById('toast');t.textContent=m;t.classList.add('show');setTimeout(()=>t.classList.remove('show'),2000);}
function copy(t){navigator.clipboard.writeText(t).then(()=>toast('کپی شد '));}
function esc(s){return (s||'').replace(/[&<>\"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;'}[c]));}
async function load(pw){
  var url='/api/public/sub/'+KEY;if(pw)url+='?pw='+encodeURIComponent(pw);
  var r=await fetch(url);var d=await r.json();
  if(d.locked){renderLock(d.name);return;}
  DATA=d;render(d);
}
function renderLock(name){
  document.getElementById('app').innerHTML='<div class="card locked"><div style=font-size:40px;margin-bottom:16px>(قفل)</div><h2 style=margin-bottom:8px>'+esc(name)+'</h2><p style=color:var(--text-muted);margin-bottom:24px>گروه دارای رمز عبور است</p><input id=pw type=password placeholder="رمز عبور" style=margin-bottom:16px><button class=btn style=width:100% onclick="load(document.getElementById(\\'pw\\').value)">باز کردن قفل</button></div>';
}
function render(d){
  var h='<div class=head><div class=logo>OX</div><h1>'+esc(d.name)+'</h1><p>'+esc(d.desc||'اشتراک اختصاصی')+'</p></div>';
  h+='<div class=metrics><div class="metric"><b>'+d.links.length+'</b><span>کانفیگ فعال</span></div><div class="metric"><b>'+d.active_connections+'</b><span>اتصال زنده</span></div><div class="metric"><b>'+d.total_used_fmt+'</b><span>کل مصرف</span></div></div>';
  h+='<div class=subbar><button class=btn style=flex:1;padding:12px;font-size:14px onclick="copy(\\''+d.sub_url+'\\')">کپی لینک اصلی اشتراک</button></div>';
  d.links.forEach((l,i)=>{
    var pct=l.limit_bytes>0?Math.min(100,l.used_bytes/l.limit_bytes*100):6;
    var st=l.active?'<span class="chip ok">فعال</span>':'<span class="chip err">منقضی</span>';
    h+='<div class="card item"><div class=top><b>'+esc(l.label)+'</b><div style=display:flex;gap:8px>'+st+'<span class="chip proto">'+esc(l.protocol)+'</span></div></div>';
    h+='<div class=bar><i style=width:'+pct+'%></i></div><div class=meta><span>مصرف: '+l.used_fmt+' / '+l.limit_fmt+'</span><span>'+l.connections+' اتصال</span></div>';
    h+='<div class=acts><button class="btn sm ghost" onclick="showQR('+i+')">QR و لینک‌ها</button><button class="btn sm ghost" onclick="copy(\\''+l.sub_url+'\\')">کپی اشتراک</button></div></div>';
  });
  document.getElementById('app').innerHTML=h;
}
function showQR(i){
  var l=DATA.links[i];document.getElementById('mTitle').textContent=l.label;
  var qb=document.getElementById('qrbox');qb.innerHTML='';
  new QRCode(qb,{text:l.sub_url,width:200,height:200,correctLevel:QRCode.CorrectLevel.M});
  var ll=document.getElementById('mLinks');ll.innerHTML='';
  (l.links||[l.vless_link]).forEach(u=>{var row=document.createElement('div');row.className='linkrow';row.innerHTML='<span style="font-family:monospace">'+esc(u)+'</span>';var b=document.createElement('button');b.className='btn sm ghost';b.textContent='کپی';b.onclick=()=>copy(u);row.appendChild(b);ll.appendChild(row);});
  document.getElementById('modalBg').classList.add('show');
}
function closeModal(){document.getElementById('modalBg').classList.remove('show');}
load();
</script></body></html>"""


DASHBOARD_HTML = """<!doctype html><html lang=fa dir=rtl><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>OXNET • داشبورد</title>__THEME_JS__
<script src="https://cdn.jsdelivr.net/npm/qrcodejs@1.0.0/qrcode.min.js"></script>
<style>__CSS__
.shell{display:flex;min-height:100vh}
.side{width:240px;flex-shrink:0;padding:24px 16px;position:sticky;top:0;height:100vh;display:flex;flex-direction:column;gap:8px;border-left:1px solid var(--border);background:var(--bg-card)}
.brand{display:flex;align-items:center;gap:12px;padding:8px 8px 32px}
.brand .b{width:40px;height:40px;border-radius:10px;background:var(--primary);display:grid;place-items:center;font-weight:800;color:var(--bg);font-size:18px}
.brand h2{margin:0;font-size:18px;font-weight:800}.brand small{color:var(--text-muted);font-size:12px;font-weight:600}
.nav{display:flex;flex-direction:column;gap:4px;flex:1}
.nav a{display:flex;align-items:center;gap:12px;padding:10px 14px;border-radius:8px;color:var(--text-muted);text-decoration:none;font-size:14px;font-weight:600;cursor:pointer;transition:all .2s}
.nav a:hover{background:var(--bg);color:var(--text-main)}
.nav a.active{background:var(--bg);color:var(--primary);border:1px solid var(--border)}
.nav a .ic{font-size:16px;opacity:0.8;font-family:sans-serif}
.side .foot{display:flex;flex-direction:column;gap:8px}
.main{flex:1;padding:32px 40px;max-width:100%;overflow-x:hidden}
.topbar{display:flex;justify-content:space-between;align-items:center;margin-bottom:32px;gap:16px;flex-wrap:wrap}
.topbar h1{margin:0;font-size:24px;font-weight:800}
.topbar .live{display:flex;align-items:center;gap:8px;color:var(--text-muted);font-size:13px;font-weight:600;background:var(--bg-card);padding:6px 12px;border-radius:8px;border:1px solid var(--border)}
.dot{width:8px;height:8px;border-radius:50%;background:var(--success);box-shadow:0 0 0 0 rgba(16,185,129,.4);animation:blink 2s infinite}
@keyframes blink{0%{box-shadow:0 0 0 0 rgba(16,185,129,.4)}70%{box-shadow:0 0 0 8px rgba(16,185,129,0)}100%{box-shadow:0 0 0 0 rgba(16,185,129,0)}}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:16px;margin-bottom:32px}
.stat{padding:20px;position:relative;overflow:hidden;border-radius:var(--radius);border:1px solid var(--border);background:var(--bg-card)}
.stat b{display:block;font-size:28px;margin-top:6px;font-weight:700;color:var(--text-main)}
.stat span{color:var(--text-muted);font-size:13px;font-weight:600}
.panel{padding:24px;margin-bottom:24px;background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius)}
.panel h3{margin:0 0 20px;font-size:16px;display:flex;align-items:center;gap:8px;font-weight:700}
.row{display:flex;gap:12px;flex-wrap:wrap}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.grid3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px}
@media(max-width:900px){.grid2,.grid3{grid-template-columns:1fr}.side{width:70px}.brand h2,.brand small,.nav a span,.side .foot .btn span{display:none}.nav a{justify-content:center;padding:10px 0}.main{padding:20px}}
.toolbar{display:flex;gap:12px;margin-bottom:20px;flex-wrap:wrap;align-items:center}
.toolbar .search{flex:1;min-width:200px;position:relative}
.toolbar .search input{padding-right:36px;border-radius:8px}
.toolbar .search::before{content:'🔍';position:absolute;right:12px;top:50%;transform:translateY(-50%);opacity:.5;font-family:sans-serif;font-size:14px}
table{width:100%;border-collapse:collapse}
th,td{padding:12px 10px;text-align:right;font-size:13px;border-bottom:1px solid var(--border)}
th{color:var(--text-muted);font-weight:600;font-size:12px}
tr:hover td{background:var(--bg)}
.mini{height:6px;border-radius:3px;background:var(--border);overflow:hidden;width:100px}
.mini i{display:block;height:100%;background:var(--primary)}
.bars{display:flex;align-items:flex-end;gap:4px;height:120px;padding-top:12px}
.bars .b{flex:1;background:var(--primary);border-radius:4px 4px 0 0;min-height:2px;position:relative;opacity:.3;transition:opacity 0.2s}
.bars .b:hover{opacity:.8}
.bars .b span{position:absolute;bottom:-20px;left:0;right:0;text-align:center;font-size:10px;color:var(--text-muted);font-weight:600}
.empty{text-align:center;padding:40px;color:var(--text-muted);font-weight:600;font-size:14px}
.modal-bg{position:fixed;inset:0;background:rgba(0,0,0,.5);backdrop-filter:blur(4px);z-index:60;display:none;align-items:center;justify-content:center;padding:20px}
.modal-bg.show{display:flex}
.modal{max-width:540px;width:100%;max-height:90vh;overflow:auto;padding:28px;background:var(--bg-card);border:1px solid var(--border);border-radius:16px;animation:fade .2s}
.modal h3{margin:0 0 20px;font-size:20px;font-weight:700}
.qrmodal{max-width:400px;text-align:center}
#qrbox{background:#fff;padding:16px;border-radius:12px;display:inline-block;margin:12px 0;border:1px solid #e2e8f0}
.linklist{text-align:right;max-height:220px;overflow:auto;margin-top:12px}
.linkrow{display:flex;gap:10px;align-items:center;background:var(--bg);border:1px solid var(--border);border-radius:8px;padding:8px 12px;margin-bottom:8px;font-size:11.5px;word-break:break-all}
.linkrow span{flex:1;color:var(--text-muted)}
.toast{position:fixed;bottom:24px;left:50%;transform:translateX(-50%);background:var(--primary);color:var(--bg);padding:10px 20px;border-radius:8px;font-weight:600;font-size:13px;z-index:90;opacity:0;transition:all .3s;pointer-events:none}
.toast.show{opacity:1;transform:translateX(-50%) translateY(-5px)}
.view{display:none}.view.active{display:block;animation:fade .3s}
.switch{position:relative;display:inline-block;width:40px;height:22px}
.switch input{display:none}.slider{position:absolute;inset:0;background:var(--border);border-radius:22px;cursor:pointer;transition:.2s}
.slider:before{content:'';position:absolute;width:16px;height:16px;right:3px;top:3px;background:#fff;border-radius:50%;transition:.2s;box-shadow:0 1px 2px rgba(0,0,0,0.2)}
.switch input:checked+.slider{background:var(--success);border-color:transparent}.switch input:checked+.slider:before{transform:translateX(-18px)}
.tag-list{display:flex;gap:6px;flex-wrap:wrap}
</style></head><body>
<button class="theme-toggle" onclick="toggleTheme()">تغییر ظاهر</button>
<div class=shell>
<aside class=side>
  <div class=brand><div class=b>OX</div><div><h2>OXNET</h2><small>Admin Console</small></div></div>
  <nav class=nav id=nav>
    <a data-v=overview class=active onclick="nav('overview')"><span class=ic>📊</span><span>نمای کلی</span></a>
    <a data-v=links onclick="nav('links')"><span class=ic>⚡</span><span>کانفیگ‌ها</span></a>
    <a data-v=subs onclick="nav('subs')"><span class=ic>📁</span><span>گروه‌ها</span></a>
    <a data-v=conns onclick="nav('conns')"><span class=ic>🌐</span><span>اتصالات زنده</span></a>
    <a data-v=activity onclick="nav('activity')"><span class=ic>🔔</span><span>لاگ سیستم</span></a>
    <a data-v=settings onclick="nav('settings')"><span class=ic>⚙️</span><span>تنظیمات</span></a>
  </nav>
  <div style="flex:1"></div>
  <div class=foot>
    <button class="btn ghost" onclick=exportState()><span>پشتیبان‌گیری</span></button>
    <button class="btn ghost" onclick=logout()><span>خروج امن</span></button>
  </div>
</aside>
<main class=main>
<div class=topbar><h1 id=vtitle>نمای کلی</h1><div class=live><span class=dot></span><span id=uptime>درحال اتصال...</span></div></div>

<section class="view active" id=v-overview>
  <div class=stats id=statsGrid></div>
<div class=panel style="margin-bottom:24px">
  <h3>🖥️ مانیتورینگ منابع سرور</h3>
  <div class=stats style="grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:16px;">
    <div class="stat" style="text-align:center; padding:16px">
      <span style="font-size:12px; color:var(--text-muted)">مصرف CPU</span>
      <b id="sysCpu" style="font-size:22px; color:var(--primary)">0%</b>
    </div>
    <div class="stat" style="text-align:center; padding:16px">
      <span style="font-size:12px; color:var(--text-muted)">مصرف RAM</span>
      <b id="sysMem" style="font-size:22px; color:var(--primary)">0%</b>
      <div style="font-size:10px; margin-top:4px" id="sysMemText">0 / 0 GB</div>
    </div>
    <div class="stat" style="text-align:center; padding:16px">
      <span style="font-size:12px; color:var(--text-muted)">هارد دیسک</span>
      <b id="sysDisk" style="font-size:22px; color:var(--primary)">0%</b>
    </div>
  </div>
</div>

  <div class=panel><h3>ترافیک ۲۴ ساعت اخیر</h3><div class=bars id=bars></div></div>
  <div class=panel><h3>رویدادهای اخیر</h3><div id=recentAct></div></div>
</section>

<section class=view id=v-links>
  <div class=toolbar>
    <button class=btn onclick=openLinkModal()>کانفیگ جدید</button>
    <div class=search><input id=linkSearch placeholder="جستجو در نام و پروتکل…" oninput=renderLinks()></div>
  </div>
  <div class=panel style="padding:10px"><table><thead><tr><th>نام و مسیر</th><th>پروتکل</th><th>مصرف حجم</th><th>اتصال</th><th>وضعیت</th><th>عملیات</th></tr></thead><tbody id=linksBody></tbody></table><div class=empty id=linksEmpty style=display:none>هیچ کانفیگی یافت نشد</div></div>
</section>

<section class=view id=v-subs>
  <div class=toolbar><button class=btn onclick=openSubModal()>گروه جدید</button></div>
  <div id=subsWrap></div>
</section>

<section class=view id=v-conns>
  <div class=panel style="padding:10px"><table><thead><tr><th>آی‌پی (IP)</th><th>کانفیگ متصل</th><th>پروتکل‌ها</th><th>جلسات</th><th>حجم تبادلی</th></tr></thead><tbody id=connsBody></tbody></table><div class=empty id=connsEmpty style=display:none>هیچ اتصالی برقرار نیست</div></div>
</section>

<section class=view id=v-activity>
  <div class=panel id=activityWrap style="padding:10px"></div>
</section>


<section class=view id=v-settings>
  <div class=panel style=max-width:500px>
    <h3>مدیریت دسترسی و امنیت</h3>
    <div class=field style=margin-bottom:12px><label>مسیر ورود به پنل (Login Path)</label><input id=set_loginpath placeholder="مثلا /my-secret-admin"></div>
    <div class=field style=margin-bottom:16px><label>کلید اتصال ربات (API Key)</label><input id=set_apikey placeholder="یک کلید امن وارد کنید"></div>
    <button class=btn onclick=saveSysSettings()>ذخیره تنظیمات امنیتی</button>
    <p id=sysMsg style=font-size:13px;margin-top:10px;font-weight:600></p>
  </div>
  <div class=panel style=max-width:500px>
    <h3>مدیریت رمز عبور</h3>
    <div class=field style=margin-bottom:12px><label>رمز عبور فعلی</label><input type=password id=curPw></div>
    <div class=field style=margin-bottom:16px><label>رمز عبور جدید</label><input type=password id=newPw></div>
    <button class=btn onclick=changePw()>ذخیره تغییرات</button>
    <p id=pwMsg style=font-size:13px;margin-top:10px;font-weight:600></p>
  </div>
  <div class=panel style=max-width:500px>
    <h3>فایل پشتیبان</h3>
    <p style=color:var(--text-muted);font-size:13px;margin-bottom:16px>تهیه خروجی کامل از دیتابیس کانفیگ‌ها و تنظیمات.</p>
    <div class=row><button class="btn ghost" onclick=exportState()>دانلود (JSON)</button><label class="btn ghost" style=cursor:pointer>آپلود (Restore)<input type=file id=importFile accept=.json style=display:none onchange=importState(event)></label></div>
  </div>
</section>

</main></div>

<div class=modal-bg id=modalBg onclick="if(event.target===this)closeModal()"><div class="modal" id=modalContent></div></div>
<div class=modal-bg id=qrBg onclick="if(event.target===this)closeQR()"><div class="modal qrmodal"><h3 id=qrTitle></h3><div id=qrbox></div><div class=linklist id=qrLinks></div><button class="btn ghost" style=width:100%;margin-top:12px onclick=closeQR()>بستن</button></div></div>
<div class=toast id=toast></div>
<script>
var LINKS=[],SUBS=[],PROTOS=[],FPS=[],DEFPROTO='multi-protocol';
function toast(m){var t=document.getElementById('toast');t.textContent=m;t.classList.add('show');setTimeout(()=>t.classList.remove('show'),2000);}
function copy(t){navigator.clipboard.writeText(t).then(()=>toast('کپی شد'));}
function esc(s){return (s==null?'':(''+s)).replace(/[&<>\"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;'}[c]));}
function api(u,o){o=o||{};o.headers=Object.assign({'Content-Type':'application/json'},o.headers||{});return fetch(u,o).then(async r=>{if(r.status===401){location.href='/login';return;}var d=await r.json().catch(()=>({}));if(!r.ok)throw new Error(d.detail||'خطا');return d;});}
function nav(v){document.querySelectorAll('.nav a').forEach(a=>a.classList.toggle('active',a.dataset.v===v));document.querySelectorAll('.view').forEach(s=>s.classList.toggle('active',s.id==='v-'+v));var t={overview:'نمای کلی',links:'کانفیگ‌ها',subs:'گروه‌ها',conns:'اتصالات زنده',activity:'لاگ سیستم',settings:'تنظیمات پنل'};document.getElementById('vtitle').textContent=t[v];if(v==='conns')loadConns();if(v==='activity')loadActivity();}
async function logout(){await fetch('/api/logout',{method:'POST'});location.href='/login';}
function fmt(b){if(b<1024)return b+' B';if(b<1048576)return (b/1024).toFixed(1)+' KB';if(b<1073741824)return (b/1048576).toFixed(2)+' MB';return (b/1073741824).toFixed(2)+' GB';}

async function loadStats(){try{var d=await api('/stats');document.getElementById('uptime').textContent='آپتایم سرور: '+d.uptime;
  var g=document.getElementById('statsGrid');
  var cards=[['🌐',d.active_connections,'اتصال زنده'],['⚡',d.active_links+' / '+d.links_count,'کانفیگ فعال'],['📁',d.subs_count,'گروه اشتراک'],['💾',d.total_traffic_mb+' MB','کل ترافیک'],['🔥',d.total_requests,'تعداد درخواست'],['⚠️',d.total_errors,'خطای سیستم']];
  g.innerHTML=cards.map(c=>'<div class="stat"><b>'+c[1]+'</b><span>'+c[2]+'</span></div>').join('');
  var hrs=[];for(var i=23;i>=0;i--){var h=new Date(Date.now()-i*3600000).getHours();hrs.push((h<10?'0':'')+h+':00');}
  
  document.getElementById('sysCpu').textContent = d.sys_cpu + '%';
  document.getElementById('sysMem').textContent = d.sys_mem_percent + '%';
  document.getElementById('sysMemText').textContent = d.sys_mem_used_gb + ' / ' + d.sys_mem_total_gb + ' GB';
  document.getElementById('sysDisk').textContent = d.sys_disk_percent + '%';
\n  var mx=Math.max(1,...hrs.map(h=>d.hourly[h]||0));
  document.getElementById('bars').innerHTML=hrs.map(h=>{var v=d.hourly[h]||0;return '<div class=b style=height:'+Math.max(3,v/mx*100)+'% title="'+h+' • '+fmt(v)+'"><span>'+h.slice(0,2)+'</span></div>';}).join('');
}catch(e){}}

async function loadAll(){var d=await api('/api/links');LINKS=d.links;renderLinks();var s=await api('/api/subs');SUBS=s.subs;renderSubs();}
async function loadMeta(){try{var d=await api('/api/protocols');PROTOS=d.protocols;FPS=d.fingerprints;DEFPROTO=d.default;}catch(e){PROTOS=['multi-protocol','vless-ws','vless-xhttp-packet-up','vless-xhttp-stream-up','trojan-ws','trojan-xhttp-packet-up'];FPS=['chrome'];}}
function protoLabel(p){var m={'multi-protocol':'مولتی پروتکل','multi-auto':'چندگانه','vless-ws':'VLESS-WS','vless-xhttp-packet-up':'VLESS-XHTTP','vless-xhttp-stream-up':'VLESS-XHTTP-S','trojan-ws':'Trojan-WS','trojan-xhttp-packet-up':'Trojan-XHTTP'};return m[p]||p;}

function renderLinks(){var q=(document.getElementById('linkSearch').value||'').toLowerCase();
  var rows=LINKS.filter(l=>!q||l.label.toLowerCase().includes(q)||l.protocol.includes(q));
  var b=document.getElementById('linksBody');
  document.getElementById('linksEmpty').style.display=rows.length?'none':'block';
  b.innerHTML=rows.map(l=>{
    var pct=l.limit_bytes>0?Math.min(100,l.used_bytes/l.limit_bytes*100):5;
    var lim=l.limit_bytes>0?fmt(l.limit_bytes):'∞';
    var stat=l.expired?'<span class="chip err">منقضی</span>':(l.active?'<span class="chip ok">فعال</span>':'<span class="chip warn">غیرفعال</span>');
    return '<tr><td><b>'+esc(l.label)+'</b><div style="color:var(--text-muted);font-size:11px;margin-top:2px;font-family:monospace">/'+esc(l.path_slug)+'</div></td>'+
    '<td><span class="chip proto">'+protoLabel(l.protocol)+'</span></td>'+
    '<td><div class=mini><i style=width:'+pct+'%></i></div><div style="color:var(--text-muted);font-size:11px;margin-top:4px"><b>'+fmt(l.used_bytes)+'</b> از '+lim+'</div></td>'+
    '<td>'+l.connected_ips+(l.ip_limit>0?' / '+l.ip_limit:'')+'</td>'+
    '<td>'+stat+'</td>'+
    '<td><div class=row style="gap:6px"><button class="btn sm ghost" onclick="showQR(\\''+l.uuid+'\\')">QR</button><button class="btn sm ghost" onclick="copy(\\''+l.sub_url+'\\')">کپی</button><button class="btn sm ghost" onclick="editLink(\\''+l.uuid+'\\')">ویرایش</button><button class="btn sm ghost" onclick="delLink(\\''+l.uuid+'\\')">حذف</button></div></td></tr>';
  }).join('');
}
function protoOptions(sel){return PROTOS.map(p=>'<option value="'+p+'" '+(p===sel?'selected':'')+'>'+protoLabel(p)+'</option>').join('');}
function fpOptions(sel){return FPS.map(f=>'<option value="'+f+'" '+(f===sel?'selected':'')+'>'+f+'</option>').join('');}

function openLinkModal(){
  document.getElementById('modalContent').innerHTML=
  '<h3>ایجاد کانفیگ جدید</h3>'+
  '<div class=field style=margin-bottom:12px><label>نام کانفیگ</label><input id=f_label></div>'+
  '<div class=grid2 style=margin-bottom:12px><div><label>پروتکل</label><select id=f_proto>'+protoOptions(DEFPROTO)+'</select></div><div><label>پورت</label><input id=f_port type=number value=443></div></div>'+
  '<div class=grid3 style=margin-bottom:12px><div><label>حجم کل</label><input id=f_lim type=number placeholder=0></div><div><label>واحد حجم</label><select id=f_limu><option>GB</option><option>MB</option></select></div><div><label>اعتبار (روز)</label><input id=f_exp type=number placeholder=0></div></div>'+
  '<div class=grid3 style=margin-bottom:12px><div><label>تعداد IP</label><input id=f_ip type=number placeholder=0></div><div><label>سقف سرعت</label><input id=f_spd type=number placeholder=0></div><div><label>واحد سرعت</label><select id=f_spdu><option value=MBIT>Mbps</option><option value=MB>MB/s</option></select></div></div>'+
  '<div class=grid2 style=margin-bottom:12px><div><label>Fingerprint</label><select id=f_fp>'+fpOptions('chrome')+'</select></div><div><label>مسیر سفارشی</label><input id=f_path placeholder="خودکار"></div></div>'+
  '<div class=field style=margin-bottom:20px><label>گروه اشتراک</label><select id=f_sub><option value="">-- مستقل --</option>'+SUBS.map(s=>'<option value="'+s.sub_id+'">'+esc(s.name)+'</option>').join('')+'</select></div>'+
  '<div class=row><button class=btn style=flex:1 onclick=createLink()>ساخت کانفیگ</button><button class="btn ghost" onclick=closeModal()>انصراف</button></div>';
  showModal();
}
async function createLink(){try{var body={label:val('f_label'),protocol:val('f_proto'),port:val('f_port'),limit_value:val('f_lim'),limit_unit:val('f_limu'),expires_days:val('f_exp'),ip_limit:val('f_ip'),speed_limit_value:val('f_spd'),speed_limit_unit:val('f_spdu'),fingerprint:val('f_fp'),path_slug:val('f_path'),sub_id:val('f_sub')||null};await api('/api/links',{method:'POST',body:JSON.stringify(body)});closeModal();toast('ساخته شد');loadAll();}catch(e){toast(e.message);}}
function val(id){return document.getElementById(id).value;}

function editLink(uuid){var l=LINKS.find(x=>x.uuid===uuid);if(!l)return;
  document.getElementById('modalContent').innerHTML='<h3>ویرایش کانفیگ</h3>'+
  '<div class=field style=margin-bottom:12px><label>نام</label><input id=e_label value="'+esc(l.label)+'"></div>'+
  '<div class=grid2 style=margin-bottom:12px><div><label>پروتکل</label><select id=e_proto>'+protoOptions(l.protocol)+'</select></div><div><label>پورت</label><input id=e_port type=number value='+(l.port||443)+'></div></div>'+
  '<div class=grid3 style=margin-bottom:12px><div><label>محدودیت IP</label><input id=e_ip type=number value='+(l.ip_limit||0)+'></div><div><label>سرعت (Mbps)</label><input id=e_spd type=number value='+(l.speed_limit_bytes?(l.speed_limit_bytes*8/1048576).toFixed(1):0)+'></div><div><label>Fingerprint</label><select id=e_fp>'+fpOptions(l.fingerprint)+'</select></div></div>'+
  '<div class=field style=margin-bottom:16px><label>مسیر سفارشی</label><input id=e_path value="'+esc(l.path_slug)+'"></div>'+
  '<div class=field style=margin-bottom:24px;display:flex;align-items:center;justify-content:space-between;background:var(--bg);padding:12px 16px;border-radius:8px;border:1px solid var(--border)><span style="font-weight:600;font-size:14px">وضعیت (روشن/خاموش)</span><label class=switch><input type=checkbox id=e_active '+(l.active?'checked':'')+'><span class=slider></span></label></div>'+
  '<div class=row><button class=btn style=flex:1 onclick="saveLink(\\''+uuid+'\\')">ذخیره</button><button class="btn ghost" onclick=closeModal()>انصراف</button></div>';
  showModal();
}
async function saveLink(uuid){try{var body={label:val('e_label'),protocol:val('e_proto'),port:val('e_port'),ip_limit:val('e_ip'),speed_limit_value:val('e_spd'),speed_limit_unit:'MBIT',fingerprint:val('e_fp'),path_slug:val('e_path'),active:document.getElementById('e_active').checked};await api('/api/links/'+uuid,{method:'PATCH',body:JSON.stringify(body)});closeModal();toast('ذخیره شد');loadAll();}catch(e){toast(e.message);}}
async function delLink(uuid){if(!confirm('حذف کانفیگ انجام شود؟'))return;try{await api('/api/links/'+uuid,{method:'DELETE'});toast('حذف شد');loadAll();}catch(e){toast(e.message);}}

function showQR(uuid){var l=LINKS.find(x=>x.uuid===uuid);if(!l)return;
  document.getElementById('qrTitle').textContent=l.label;var qb=document.getElementById('qrbox');qb.innerHTML='';
  new QRCode(qb,{text:l.sub_url,width:200,height:200,correctLevel:QRCode.CorrectLevel.M});
  var ll=document.getElementById('qrLinks');ll.innerHTML='';
  addRow(ll,l.sub_url,'لینک اشتراک');(l.links||[]).forEach((u,i)=>addRow(ll,u,'پروتکل '+(i+1)));
  document.getElementById('qrBg').classList.add('show');
}
function addRow(ll,u,tag){var row=document.createElement('div');row.className='linkrow';row.innerHTML='<span><b style="font-size:13px">'+tag+'</b><br><span style="font-family:monospace;font-size:11px;color:var(--text-muted)">'+esc(u)+'</span></span><button class="btn sm ghost" onclick="copy(\\''+u+'\\')">کپی</button>';ll.appendChild(row);}
function closeQR(){document.getElementById('qrBg').classList.remove('show');}

function renderSubs(){var w=document.getElementById('subsWrap');if(!SUBS.length){w.innerHTML='<div class="panel empty">هیچ گروهی ایجاد نشده است.</div>';return;}
  w.innerHTML=SUBS.map(s=>'<div class=panel><div class=row style="justify-content:space-between;align-items:center"><div><h3 style="margin:0;font-size:18px">'+esc(s.name)+(s.has_password?' <span style="opacity:0.6">(قفل)</span>':'')+'</h3><div style="color:var(--text-muted);font-size:12px;margin-top:4px">'+esc(s.desc||'')+' • '+s.links_count+' زیرمجموعه • '+s.total_used_fmt+'</div></div><div class=row style=gap:8px><button class="btn sm ghost" onclick="copy(\\''+s.public_url+'\\')">صفحه عمومی</button><button class="btn sm ghost" onclick="copy(\\''+s.sub_url+'\\')">کپی لینک</button><button class="btn sm danger" onclick="delSub(\\''+s.sub_id+'\\')">حذف</button></div></div></div>').join('');
}
function openSubModal(){document.getElementById('modalContent').innerHTML='<h3>ایجاد گروه</h3><div class=field style=margin-bottom:12px><label>نام</label><input id=s_name></div><div class=field style=margin-bottom:12px><label>توضیحات</label><input id=s_desc></div><div class=field style=margin-bottom:20px><label>رمز صفحه عمومی</label><input id=s_pw type=password></div><div class=row><button class=btn style=flex:1 onclick=createSub()>ساخت گروه</button><button class="btn ghost" onclick=closeModal()>انصراف</button></div>';showModal();}
async function createSub(){try{await api('/api/subs',{method:'POST',body:JSON.stringify({name:val('s_name'),desc:val('s_desc'),password:val('s_pw')})});closeModal();toast('ساخته شد');loadAll();}catch(e){toast(e.message);}}
async function delSub(id){if(!confirm('گروه حذف شود؟'))return;try{await api('/api/subs/'+id,{method:'DELETE'});toast('حذف شد');loadAll();}catch(e){toast(e.message);}}

async function loadConns(){try{var d=await api('/api/connections');var b=document.getElementById('connsBody');document.getElementById('connsEmpty').style.display=d.connections.length?'none':'block';
  b.innerHTML=d.connections.map(c=>'<tr><td><b style="font-family:monospace;font-size:13px">'+esc(c.ip)+'</b></td><td><span style="font-weight:600">'+esc(c.label)+'</span></td><td><div class=tag-list>'+c.transports.map(t=>'<span class="chip proto">'+esc(t)+'</span>').join('')+'</div></td><td>'+c.sessions+'</td><td><b>'+c.bytes_fmt+'</b></td></tr>').join('');
}catch(e){}}
async function loadActivity(){try{var d=await api('/api/activity');var lv={ok:'ok',err:'err',warn:'warn',info:'info'};document.getElementById('activityWrap').innerHTML=d.logs.slice().reverse().map(l=>'<div class=row style="justify-content:space-between;padding:10px 4px;border-bottom:1px solid var(--border);align-items:center"><span style="font-size:13px"><span class="chip '+(lv[l.level]||'info')+'" style="margin-left:6px">'+esc(l.kind)+'</span> '+esc(l.message)+'</span><span style="color:var(--text-muted);font-size:11px;font-family:monospace">'+new Date(l.time).toLocaleString('fa-IR')+'</span></div>').join('')||'<div class=empty>بدون رویداد</div>';}catch(e){}}
function renderRecent(){api('/api/activity').then(d=>{document.getElementById('recentAct').innerHTML=d.logs.slice(-6).reverse().map(l=>'<div class=row style="justify-content:space-between;padding:8px 4px;border-bottom:1px solid var(--border);align-items:center"><span style="font-size:13px;font-weight:600">'+esc(l.message)+'</span><span style="color:var(--text-muted);font-size:11px">'+new Date(l.time).toLocaleTimeString('fa-IR')+'</span></div>').join('')||'<div class=empty>—</div>';}).catch(()=>{});}


async function loadSysSettings(){try{var d=await api('/api/sys-settings');document.getElementById('set_loginpath').value=d.login_path;document.getElementById('set_apikey').value=d.api_key;}catch(e){}}
async function saveSysSettings(){var m=document.getElementById('sysMsg');try{await api('/api/sys-settings',{method:'POST',body:JSON.stringify({login_path:val('set_loginpath'),api_key:val('set_apikey')})});m.style.color='var(--success)';m.textContent='انجام شد (احتمالاً نیاز به لاگین مجدد دارید)';}catch(e){m.style.color='var(--danger)';m.textContent=e.message;}}

async function changePw(){var m=document.getElementById('pwMsg');try{await api('/api/change-password',{method:'POST',body:JSON.stringify({current_password:val('curPw'),new_password:val('newPw')})});m.style.color='var(--success)';m.textContent='انجام شد';}catch(e){m.style.color='var(--danger)';m.textContent=e.message;}}
async function exportState(){try{var d=await api('/api/export');var blob=new Blob([JSON.stringify(d,null,2)],{type:'application/json'});var a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='oxnet-backup.json';a.click();toast('دانلود شد');}catch(e){toast(e.message);}}
function importState(e){var f=e.target.files[0];if(!f)return;var rd=new FileReader();rd.onload=async()=>{try{var body=JSON.parse(rd.result);var r=await api('/api/import',{method:'POST',body:JSON.stringify(body)});toast('وارد شد');loadAll();}catch(x){toast('نامعتبر');}};rd.readAsText(f);}

function showModal(){document.getElementById('modalBg').classList.add('show');}
function closeModal(){document.getElementById('modalBg').classList.remove('show');}

(async function(){await loadMeta();await loadAll();loadStats();loadSysSettings();renderRecent();setInterval(loadStats,5000);setInterval(renderRecent,8000);setInterval(()=>{if(document.getElementById('v-conns').classList.contains('active'))loadConns();},5000);})();
</script></body></html>""".replace("__CSS__", _BASE_CSS).replace("__THEME_JS__", _THEME_JS)
