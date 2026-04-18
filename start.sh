#!/bin/bash
# تشغيل الموقع
gunicorn src.main:app &

# تشغيل البوت
python bot/bot_updated.py &

# انتظار كلا العمليتين
wait
