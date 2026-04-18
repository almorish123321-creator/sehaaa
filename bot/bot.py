#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Seha Sick Leave Bot - Fast Input Version
بوت تيليجرام يدعم الإدخال السريع (رسالة واحدة)
"""

import logging
import os
import re
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import BOT_TOKEN, ADMIN_USER_ID, OUTPUT_DIR
from pdf_generator_v4 import generate_sick_leave_pdf
from api_client import send_leave_data_to_api

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# حالات المحادثة
STATES = {
    'START': 0,
    'LOGO_UPLOAD': 20
}

# تخزين بيانات المستخدمين
user_data = {}

def parse_bulk_data(text: str) -> dict:
    """تحويل النص إلى قاموس بيانات (للإدخال السريع)"""
    data = {}
    
    for line in text.strip().split('\n'):
        if ':' in line:
            parts = line.split(':', 1)
            key = parts[0].strip().lower().replace(' ', '_').replace('(', '').replace(')', '')
            value = parts[1].strip()
            
            # اسم المريض
            if 'اسم_المريض' in key and 'عربي' in line:
                data['patient_name_ar'] = value
            elif 'اسم_المريض' in key and 'إنجليزي' in line:
                data['patient_name_en'] = value
            # رقم الهوية
            elif 'رقم_الهوية' in key or 'الهوية' in key:
                data['id_number'] = value
            # الجنسية
            elif 'الجنسية' in key and 'عربي' in line:
                data['nationality_ar'] = value
            elif 'الجنسية' in key and 'إنجليزي' in line:
                data['nationality_en'] = value
            # جهة العمل
            elif 'جهة_العمل' in key and 'عربي' in line:
                data['employer_ar'] = value
            elif 'جهة_العمل' in key and 'إنجليزي' in line:
                data['employer_en'] = value
            # اسم الطبيب
            elif 'اسم_الطبيب' in key and 'عربي' in line:
                data['doctor_name_ar'] = value
            elif 'اسم_الطبيب' in key and 'إنجليزي' in line:
                data['doctor_name_en'] = value
            # المسمى الوظيفي
            elif 'المسمى_الوظيفي' in key and 'عربي' in line:
                data['position_ar'] = value
            elif 'المسمى_الوظيفي' in key and 'إنجليزي' in line:
                data['position_en'] = value
            # التواريخ
            elif 'تاريخ_الدخول' in key and 'ميلادي' in line:
                data['admission_date_gregorian'] = value
            elif 'تاريخ_الدخول' in key and 'هجري' in line:
                data['admission_date_hijri'] = value
            elif 'تاريخ_الخروج' in key and 'ميلادي' in line:
                data['discharge_date_gregorian'] = value
            elif 'تاريخ_الخروج' in key and 'هجري' in line:
                data['discharge_date_hijri'] = value
            elif 'تاريخ_إصدار_التقرير' in key:
                data['issue_date_gregorian'] = value
            # المنشأة
            elif 'اسم_المنشأة' in key and 'عربي' in line:
                data['hospital_name_ar'] = value
            elif 'اسم_المنشأة' in key and 'إنجليزي' in line:
                data['hospital_name_en'] = value
            # الوقت
            elif 'الوقت' in key:
                data['time'] = value
    
    return data if data else None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج أمر /start"""
    user_id = update.effective_user.id
    
    welcome_message = """👋 مرحبًا بك في بوت منصة صحة

🚀 **الإدخال السريع (رسالة واحدة):**
أرسل جميع البيانات بهذا التنسيق:

اسم المريض (عربي): أحمد محمد
رقم الهوية: 1234567890
اسم الطبيب (عربي): د. خالد
اسم المنشأة (عربي): المستشفى
تاريخ الدخول (ميلادي): 18-04-2026
تاريخ الخروج (ميلادي): 20-04-2026

📝 **أو اضغط الزر لبدء تقرير جديد خطوة بخطوة**

لبدء إنشاء تقرير، اضغط الزر أدناه:"""
    
    keyboard = [[KeyboardButton("🆕 إنشاء تقرير جديد")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    
    await update.message.reply_text(welcome_message, reply_markup=reply_markup)
    user_data[user_id] = {'state': STATES['START']}

async def generate_pdf_report(update: Update, context: ContextTypes.DEFAULT_TYPE, data: dict, user_id: int) -> None:
    """توليد تقرير PDF وإرساله"""
    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        pdf_path = generate_sick_leave_pdf(data, user_id)
        
        if pdf_path and os.path.exists(pdf_path):
            with open(pdf_path, 'rb') as pdf_file:
                await update.message.reply_document(
                    document=pdf_file,
                    filename=os.path.basename(pdf_path),
                    caption="✅ تم إنشاء تقرير الإجازة المرضية بنجاح!"
                )
            
            # إرسال البيانات إلى API
            try:
                api_result = send_leave_data_to_api(data)
                if api_result and api_result.get('success'):
                    await update.message.reply_text(f"✅ تم حفظ البيانات في النظام بنجاح!\n🆔 رمز الإجازة: {api_result.get('leave_id', 'غير محدد')}")
                else:
                    await update.message.reply_text(f"⚠️ تم إنشاء التقرير ولكن حدث خطأ: {api_result.get('message', 'غير معروف')}")
            except Exception as api_error:
                logger.warning(f"خطأ في إرسال البيانات إلى API: {api_error}")
        else:
            await update.message.reply_text("❌ حدث خطأ في توليد التقرير.")
            
    except Exception as e:
        logger.error(f"خطأ في توليد PDF: {e}")
        await update.message.reply_text("❌ حدث خطأ في توليد التقرير.")

async def handle_bulk_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج استلام البيانات بصيغة واحدة"""
    user_id = update.effective_user.id
    data = parse_bulk_data(update.message.text)
    
    if data and len(data) >= 3:
        user_data[user_id] = {'data': data}
        
        summary = f"""📝 تم استلام البيانات بنجاح!

👤 اسم المريض: {data.get('patient_name_ar', 'غير محدد')}
🆔 رقم الهوية: {data.get('id_number', 'غير محدد')}
🏥 المنشأة: {data.get('hospital_name_ar', 'غير محدد')}
👨‍⚕️ الطبيب: {data.get('doctor_name_ar', 'غير محدد')}

📎 أرسل شعار المنشأة (صورة) الآن لإكمال التقرير."""
        
        await update.message.reply_text(summary)
    else:
        await update.message.reply_text("❌ لم أتمكن من تحليل البيانات.\n\nالتنسيق المطلوب:\nاسم المريض (عربي): أحمد\nرقم الهوية: 123456\nاسم الطبيب (عربي): د. خالد")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج الصور المرسلة (الشعار)"""
    user_id = update.effective_user.id
    
    if user_id in user_data and 'data' in user_data[user_id]:
        try:
            await update.message.reply_text("🔄 جاري إنشاء التقرير...")
            
            # حفظ الصورة
            photo = update.message.photo[-1]
            file = await context.bot.get_file(photo.file_id)
            
            logos_dir = f"{OUTPUT_DIR}/logos"
            os.makedirs(logos_dir, exist_ok=True)
            
            logo_path = f"{logos_dir}/logo_{user_id}.jpg"
            await file.download_to_drive(logo_path)
            
            # إضافة الشعار إلى البيانات
            data = user_data[user_id]['data']
            data['custom_logo'] = logo_path
            
            # توليد التقرير
            await generate_pdf_report(update, context, data, user_id)
            
            # تنظيف بيانات المستخدم
            del user_data[user_id]
            
            keyboard = [[KeyboardButton("🆕 إنشاء تقرير جديد")]]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
            await update.message.reply_text("يمكنك إنشاء تقرير جديد:", reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"خطأ في معالجة الشعار: {e}")
            await update.message.reply_text("❌ حدث خطأ. يرجى المحاولة مرة أخرى.")
    else:
        await update.message.reply_text("🖼️ يرجى أولاً إرسال البيانات المنسقة أو اضغط /start")

async def handle_new_report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج زر إنشاء تقرير جديد"""
    await update.message.reply_text("📝 يرجى إرسال جميع البيانات في رسالة واحدة بالتنسيق المذكور في رسالة /start")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج الرسائل النصية الرئيسي"""
    message_text = update.message.text
    
    if message_text == "🆕 إنشاء تقرير جديد":
        await handle_new_report(update, context)
        return
    
    # محاولة تحليل البيانات
    data = parse_bulk_data(message_text)
    if data and len(data) >= 3:
        await handle_bulk_message(update, context)
        return
    
    await update.message.reply_text("❌ لم أتمكن من تحليل البيانات.\n\nأرسل /start لمعرفة التنسيق الصحيح.")

def main() -> None:
    """الدالة الرئيسية لتشغيل البوت"""
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    print("🤖 بدء تشغيل بوت صحة - النسخة السريعة...")
    print("✅ يدعم استقبال البيانات في رسالة واحدة")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
