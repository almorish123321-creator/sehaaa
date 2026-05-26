#!/bin/bash
# سكريبت تشغيل البوت على Termux
# Run: chmod +x start_bot.sh && ./start_bot.sh

echo "🤖 إعداد بوت صحة على Termux..."

# تحديث الحزم
pkg update -y && pkg upgrade -y

# تثبيت Python
pkg install python -y

# تثبيت المتطلبات
pip install -r requirements.txt

# العودة لمجلد المشروع
cd "$(dirname "$0")/.."

# تشغيل البوت
echo "🚀 بدء تشغيل البوت..."
python3 bot/bot.py
