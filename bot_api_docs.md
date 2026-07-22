# OXNET Bot API Documentation (v4.0)

شما می‌توانید با استفاده از `API_KEY` سرور خود، ربات تلگرامی یا هر اپلیکیشن دیگری را مستقیماً به OXNET متصل کنید.

## احراز هویت (Authentication)
تمامی درخواست‌ها به API باید دارای هدر `X-API-Key` باشند.
- مثال هدر: `X-API-Key: YOUR_SECRET_API_KEY`

## مسیرهای API

### ۱. لیست کانفیگ‌ها
`GET /api/links`
- خروجی: لیست تمامی کانفیگ‌ها و وضعیت آن‌ها.

### ۲. ساخت کانفیگ جدید
`POST /api/links`
- نمونه Body (JSON):
```json
{
  "label": "کاربر جدید بات",
  "protocol": "multi-protocol",
  "limit_value": 10,
  "limit_unit": "GB",
  "expires_days": 30,
  "ip_limit": 2,
  "speed_limit_value": 0
}
```

### ۳. تغییر وضعیت یا حجم کانفیگ
`PATCH /api/links/{uuid}`
- ویرایش کانفیگ (فعال/غیرفعال کردن، تغییر حجم):
```json
{
  "active": false,
  "limit_value": 20
}
```
- ریست حجم مصرفی:
```json
{
  "reset_usage": true
}
```

### ۴. حذف کانفیگ
`DELETE /api/links/{uuid}`
- حذف کامل کانفیگ.

### ۵. دریافت آمار کلی سرور
`GET /stats`
- دریافت اطلاعات زنده اتصالات، مصرف رم/ترافیک و غیره.
