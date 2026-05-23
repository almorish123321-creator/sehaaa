# Configuration file for Seha Sick Leave Bot - Updated Version
# النسخة المحدثة - جميع البيانات الحساسة من متغيرات البيئة فقط

import os

# ========== قراءة كل شيء من متغيرات البيئة فقط (آمن) ==========
BOT_TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_USER_ID = int(os.environ.get('ADMIN_USER_ID', 0))  # ⚠️ غير الـ 0 إلى رقم التليغرام الخاص بك

# ========== API Settings ==========
# ضع رابط موقعك على Render هنا
API_BASE_URL = os.environ.get('API_BASE_URL', 'https://YOUR-APP-NAME.onrender.com')
API_ENDPOINT = '/api/medical-leaves'
API_FULL_URL = API_BASE_URL + API_ENDPOINT

# ========== المسارات (ثابتة) ==========
FONTS_DIR = './bot/fonts'
IMAGES_DIR = './bot'
OUTPUT_DIR = './bot/output'

# ========== باقي الإعدادات (ثابتة) ==========
NOTO_SANS_ARABIC_BOLD = f'{FONTS_DIR}/noto_sans_arabic/NotoSansArabic-Bold.ttf'
NOTO_SANS_ARABIC_REGULAR = f'{FONTS_DIR}/noto_sans_arabic/NotoSansArabic-Regular.ttf'
TIMES_NR_MT_BOLD = f'{FONTS_DIR}/times_nr_mt/TimesNRMTPro-Bold.otf'
TIMES_NR_MT_REGULAR = f'{FONTS_DIR}/times_nr_mt/TimesNRMTPro-Regular.otf'
SEHA_LOGO = f'{IMAGES_DIR}/شعارصحةseha.jpg'
GEOMETRIC_SHAPE = f'{IMAGES_DIR}/الشكلالهندسي.jpg'
KINGDOM_TEXT = f'{IMAGES_DIR}/كلمةالمملكةالعربيةالسعوديةKingdomofSaudiArabia.jpg'
HOSPITAL_LOGO = f'{IMAGES_DIR}/شعارالمستشفى.png'
HEALTH_INFO_CENTER_LOGO = f'{IMAGES_DIR}/شعارالمركزالوطنيللمعلوماتالصحية.jpg'

# ========== QR Code ==========
QR_URL = os.environ.get('QR_URL', API_BASE_URL)

# ========== PDF settings ==========
PDF_WIDTH = 297
PDF_HEIGHT = 419
