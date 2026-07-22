# OXNET v2.0

پنل مدیریت پراکسی چند‌پروتکله مبتنی بر FastAPI — بازطراحی کامل، رفع باگ‌ها و پشتیبانی از VLESS و Trojan.

## تازه‌های نسخه ۲

- **مولتی‌پروتکل (multi-protocol):** یک کانفیگ = یک ساب شامل همه‌ی پروتکل‌ها (VLESS-WS / VLESS-XHTTP / VLESS-XHTTP-Stream / Trojan-WS / Trojan-XHTTP).
- **پروتکل Trojan** روی هر دو ترانسپورت WS و XHTTP.
- تشخیص خودکار پروتکل از روی اولین بایت‌های کلاینت (یک مسیر برای هر دو).
- داشبورد کاملاً بازطراحی‌شده (glassmorphism، پس‌زمینه‌ی متحرک، RTL، نمودار ترافیک ۲۴ ساعته، جستجو، QR).
- ریست مصرف، خروجی/ورودی (backup/restore)، محدودیت IP و سرعت.

## رفع باگ‌ها

- **Deadlock محدودکننده‌ی سرعت:** سطل توکن بدهی‌محور شد (دیگر با chunk‌های بزرگ‌تر از ظرفیت قفل نمی‌شود).
- **منطقه‌ی زمانی:** همه‌جا tz-aware (Asia/Tehran) و یکدست.
- **CORS:** ترکیب نامعتبر wildcard + credentials اصلاح شد.
- اصلاح پیمایش آدرس IPv6 در پارسر VLESS.

## اجرا

```bash
pip install -r requirements.txt
python main.py
# پنل: /login  (رمز پیش‌فرض: OXNET یا متغیر ADMIN_PASSWORD)
```

## متغیرهای محیطی

| متغیر | پیش‌فرض | توضیح |
|---|---|---|
| `PORT` | 8000 | پورت سرور |
| `ADMIN_PASSWORD` | OXNET | رمز پنل |
| `SECRET_KEY` | خودکار | کلید رمزنگاری |
| `DATA_DIR` | ./data | مسیر ذخیره |
| `XHTTP_BASE_PATH` | /xhttp-oxnet | مسیر پایه‌ی XHTTP |

## ساختار

- `main.py` — مسیرها و API
- `state.py` — وضعیت، کانفیگ‌ها، مولد لینک
- `protocols.py` — پارسر VLESS/Trojan و تشخیص خودکار
- `relay_ws.py` — تونل WebSocket چند‌پروتکله
- `xhttp_oxnet.py` — ترانسپورت XHTTP
- `speed_limit.py` — محدودیت سرعت (بدهی‌محور)
- `pages.py` — رابط کاربری (لاگین / داشبورد / صفحه‌ی عمومی)

> این ابزار برای دور زدن سانسور و حفظ حریم خصوصی طراحی شده است.
