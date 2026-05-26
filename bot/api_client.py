#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Client for Seha Website Integration
عميل API لربط البوت بموقع صحة
"""

import requests
import json
import logging
from datetime import datetime
from config import API_FULL_URL

# إعداد التسجيل
logger = logging.getLogger(__name__)

def calculate_days(admission_date, discharge_date):
    """حساب عدد الأيام بين تاريخين"""
    try:
        admission_parts = admission_date.split('-')
        discharge_parts = discharge_date.split('-')
        
        if len(admission_parts) == 3 and len(discharge_parts) == 3:
            admission_dt = datetime(int(admission_parts[2]), int(admission_parts[1]), int(admission_parts[0]))
            discharge_dt = datetime(int(discharge_parts[2]), int(discharge_parts[1]), int(discharge_parts[0]))
            
            days = (discharge_dt - admission_dt).days + 1
            return max(1, days)
        else:
            return 1
    except Exception as e:
        logger.error(f"خطأ في حساب الأيام: {e}")
        return 1

def generate_leave_id(id_number, admission_date, discharge_date):
    """توليد رمز الإجازة مطابق لما يتم في PDF"""
    try:
        id_part = id_number[-4:] if len(id_number) >= 4 else id_number
        admission_nums = ''.join(filter(str.isdigit, admission_date))[-3:]
        discharge_nums = ''.join(filter(str.isdigit, discharge_date))[-4:]
        leave_number = (id_part + admission_nums + discharge_nums).ljust(11, '0')[:11]
        return f"PSL{leave_number}"
    except Exception as e:
        logger.error(f"خطأ في توليد رمز الإجازة: {e}")
        return f"PSL{id_number[-4:] if len(id_number) >= 4 else id_number}0000000"

def convert_date_format(date_str):
    """تحويل التاريخ من صيغة dd-mm-yyyy إلى yyyy-mm-dd"""
    try:
        parts = date_str.split('-')
        if len(parts) == 3:
            return f"{parts[2]}-{parts[1]}-{parts[0]}"
        return date_str
    except:
        return date_str

def send_leave_data_to_api(user_data):
    """إرسال بيانات الإجازة إلى API الموقع"""
    try:
        leave_id = generate_leave_id(
            user_data.get('id_number', ''),
            user_data.get('admission_date_gregorian', ''),
            user_data.get('discharge_date_gregorian', '')
        )
        
        report_date = convert_date_format(user_data.get('issue_date_gregorian', ''))
        entry_date = convert_date_format(user_data.get('admission_date_gregorian', ''))
        exit_date = convert_date_format(user_data.get('discharge_date_gregorian', ''))
        
        # حساب المدة
        duration_days = calculate_days(
            user_data.get('admission_date_gregorian', ''),
            user_data.get('discharge_date_gregorian', '')
        )
        
        # إعداد البيانات للإرسال - مطابق لحقول API
        api_data = {
            'service_code': leave_id,
            'identity_number': user_data.get('id_number', ''),
            'patient_name_ar': user_data.get('patient_name_ar', ''),
            'patient_name_en': user_data.get('patient_name_en', ''),
            'nationality_ar': user_data.get('nationality_ar', ''),
            'nationality_en': user_data.get('nationality_en', ''),
            'workplace_ar': user_data.get('employer_ar', ''),
            'workplace_en': user_data.get('employer_en', ''),
            'doctor_name_ar': user_data.get('doctor_name_ar', ''),
            'doctor_name_en': user_data.get('doctor_name_en', ''),
            'job_title_ar': user_data.get('position_ar', ''),
            'job_title_en': user_data.get('position_en', ''),
            'admission_date_gregorian': entry_date,
            'admission_date_hijri': user_data.get('admission_date_hijri', ''),
            'discharge_date_gregorian': exit_date,
            'discharge_date_hijri': user_data.get('discharge_date_hijri', ''),
            'report_issue_date': report_date,
            'facility_name_ar': user_data.get('hospital_name_ar', ''),
            'facility_name_en': user_data.get('hospital_name_en', ''),
            'report_time': user_data.get('time', ''),
            'duration_days': duration_days
        }
        
        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'Accept': 'application/json'
        }
        
        logger.info(f"إرسال البيانات إلى API: {API_FULL_URL}")
        logger.info(f"البيانات المرسلة: {json.dumps(api_data, ensure_ascii=False)}")
        
        response = requests.post(
            API_FULL_URL,
            json=api_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code in [200, 201]:
            try:
                result = response.json()
                logger.info(f"تم إرسال البيانات بنجاح")
                return {
                    'success': True,
                    'message': 'تم حفظ بيانات الإجازة في النظام بنجاح',
                    'leave_id': leave_id,
                    'data': result.get('data', {})
                }
            except:
                logger.info(f"تم إرسال البيانات (HTTP {response.status_code})")
                return {
                    'success': True,
                    'message': 'تم حفظ بيانات الإجازة في النظام',
                    'leave_id': leave_id
                }
        else:
            logger.error(f"خطأ HTTP {response.status_code}: {response.text}")
            return {
                'success': False,
                'message': f"خطأ في الاتصال بالخادم (HTTP {response.status_code})",
                'leave_id': leave_id
            }
            
    except requests.exceptions.ConnectionError:
        logger.error("فشل في الاتصال بالخادم")
        return {
            'success': False,
            'message': 'فشل في الاتصال بالخادم. تأكد من تشغيل الموقع.',
            'leave_id': leave_id if 'leave_id' in locals() else 'غير محدد'
        }
    except requests.exceptions.Timeout:
        logger.error("انتهت مهلة الاتصال")
        return {
            'success': False,
            'message': 'انتهت مهلة الاتصال بالخادم',
            'leave_id': leave_id if 'leave_id' in locals() else 'غير محدد'
        }
    except Exception as e:
        logger.error(f"خطأ غير متوقع في إرسال البيانات: {e}")
        return {
            'success': False,
            'message': f'خطأ غير متوقع: {str(e)}',
            'leave_id': leave_id if 'leave_id' in locals() else 'غير محدد'
        }
