#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration file for Seha Sick Leave Bot
ملف إعدادات بوت صحة - يدعم متغيرات البيئة

يتم قراءة الإعدادات من:
1. متغيرات البيئة (Environment Variables) - تُضاف من موقع الاستضافة
2. ملف .env (عبر python-dotenv) - للاستخدام المحلي
3. قيم افتراضية - في حال لم يتم تعيين المتغيرات
"""

import os
from pathlib import Path

# محاولة تحميل ملف .env للاستخدام المحلي
try:
    from dotenv import load_dotenv
    # البحث عن ملف .env في مجلد المشروع الجذري
    project_root = Path(__file__).parent.parent
    env_file = project_root / '.env'
    if env_file.exists():
        load_dotenv(env_file)
        print(f"تم تحميل ملف .env من: {env_root}")
    else:
        print("ملف .env غير موجود، يتم استخدام متغيرات البيئة المباشرة")
except ImportError:
    print("python-dotenv غير مثبت، يتم استخدام متغيرات البيئة المباشرة")

# ============================================
# === إعدادات البوت (Telegram Bot) ===
# ============================================
# أضف BOT_TOKEN و ADMIN_USER_ID من موقع الاستضافة (Render/Koyeb/Railway)
BOT_TOKEN = os.environ.get('BOT_TOKEN', '')
ADMIN_USER_ID = os.environ.get('ADMIN_USER_ID', '')

# ============================================
# === إعدادات API الموقع ===
# ============================================
# رابط الموقع المنشور - غيّره عند النشر
API_BASE_URL = os.environ.get('API_BASE_URL', 'http://localhost:5000')
API_ENDPOINT = os.environ.get('API_ENDPOINT', '/api/medical-leaves')
API_FULL_URL = API_BASE_URL + API_ENDPOINT

# ============================================
# === المسارات - ديناميكية حسب البيئة ===
# ============================================
# تحديد مجلد المشروع الجذري تلقائياً
PROJECT_ROOT = str(Path(__file__).parent.parent.resolve())

FONTS_DIR = os.environ.get('FONTS_DIR', os.path.join(PROJECT_ROOT, 'bot', 'fonts'))
IMAGES_DIR = os.environ.get('IMAGES_DIR', os.path.join(PROJECT_ROOT, 'bot'))
OUTPUT_DIR = os.environ.get('OUTPUT_DIR', os.path.join(PROJECT_ROOT, 'bot', 'output'))

# إنشاء مجلد الإخراج تلقائياً
os.makedirs(OUTPUT_DIR, exist_ok=True)

# === مسارات الخطوط ===
NOTO_SANS_ARABIC_BOLD = os.path.join(FONTS_DIR, 'noto_sans_arabic', 'NotoSansArabic-Bold.ttf')
NOTO_SANS_ARABIC_REGULAR = os.path.join(FONTS_DIR, 'noto_sans_arabic', 'NotoSansArabic-Regular.ttf')
TIMES_NR_MT_BOLD = os.path.join(FONTS_DIR, 'times_nr_mt', 'TimesNRMTPro-Bold.otf')
TIMES_NR_MT_REGULAR = os.path.join(FONTS_DIR, 'times_nr_mt', 'TimesNRMTPro-Regular.otf')

# === مسارات الصور ===
SEHA_LOGO = os.path.join(IMAGES_DIR, 'شعارصحةseha.jpg')
GEOMETRIC_SHAPE = os.path.join(IMAGES_DIR, 'الشكلالهندسي.jpg')
KINGDOM_TEXT = os.path.join(IMAGES_DIR, 'كلمةالمملكةالعربيةالسعوديةKingdomofSaudiArabia.jpg')
HOSPITAL_LOGO = os.path.join(IMAGES_DIR, 'شعارالمستشفى.png')
HEALTH_INFO_CENTER_LOGO = os.path.join(IMAGES_DIR, 'شعارالمركزالوطنيللمعلوماتالصحية.jpg')

# ============================================
# === إعدادات QR Code ===
# ============================================
QR_URL = os.environ.get('QR_URL', 'https://www.seha.sa/#/inquiries/slenquiry')

# ============================================
# === إعدادات PDF ===
# ============================================
PDF_WIDTH = int(os.environ.get('PDF_WIDTH', '297'))  # mm
PDF_HEIGHT = int(os.environ.get('PDF_HEIGHT', '419'))  # mm

# ============================================
# === التحقق من الإعدادات الحرجة ===
# ============================================
def validate_config():
    """التحقق من الإعدادات الحرجة عند بدء التشغيل"""
    errors = []
    
    if not BOT_TOKEN:
        errors.append("BOT_TOKEN غير محدد! أضفه من موقع الاستضافة أو ملف .env")
    
    if not ADMIN_USER_ID:
        errors.append("ADMIN_USER_ID غير محدد! أضفه من موقع الاستضافة أو ملف .env")
    
    # فحص وجود الخطوط
    missing_fonts = []
    for name, path in [
        ('NotoSansArabic-Bold', NOTO_SANS_ARABIC_BOLD),
        ('NotoSansArabic-Regular', NOTO_SANS_ARABIC_REGULAR),
        ('TimesNRMT-Bold', TIMES_NR_MT_BOLD),
        ('TimesNRMT-Regular', TIMES_NR_MT_REGULAR),
    ]:
        if not os.path.exists(path):
            missing_fonts.append(name)
    
    if missing_fonts:
        print(f"تحذير: خطوط مفقودة: {', '.join(missing_fonts)}")
    
    # فحص وجود الصور
    missing_images = []
    for name, path in [
        ('SEHA_LOGO', SEHA_LOGO),
        ('GEOMETRIC_SHAPE', GEOMETRIC_SHAPE),
        ('KINGDOM_TEXT', KINGDOM_TEXT),
    ]:
        if not os.path.exists(path):
            missing_images.append(name)
    
    if missing_images:
        print(f"تحذير: صور مفقودة: {', '.join(missing_images)}")
    
    if errors:
        print("=" * 50)
        print("أخطاء في الإعدادات:")
        for error in errors:
            print(f"  - {error}")
        print("=" * 50)
    
    return len(errors) == 0

# طباعة الإعدادات عند التشغيل
if __name__ == '__main__':
    print("إعدادات مشروع صحة:")
    print(f"  BOT_TOKEN: {'***' + BOT_TOKEN[-6:] if BOT_TOKEN and len(BOT_TOKEN) > 6 else 'غير محدد'}")
    print(f"  ADMIN_USER_ID: {ADMIN_USER_ID or 'غير محدد'}")
    print(f"  API_BASE_URL: {API_BASE_URL}")
    print(f"  API_FULL_URL: {API_FULL_URL}")
    print(f"  PROJECT_ROOT: {PROJECT_ROOT}")
    print(f"  FONTS_DIR: {FONTS_DIR}")
    print(f"  IMAGES_DIR: {IMAGES_DIR}")
    print(f"  OUTPUT_DIR: {OUTPUT_DIR}")
    validate_config()
