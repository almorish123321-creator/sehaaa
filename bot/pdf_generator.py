#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced PDF Generator for Seha Sick Leave Reports with Arabic Text Support
وحدة توليد تقارير الإجازة المرضية بصيغة PDF
"""

import os
import qrcode
from datetime import datetime
from fpdf import FPDF
from PIL import Image
from config import *
import arabic_reshaper
from bidi.algorithm import get_display

class SickLeavePDF(FPDF):
    def __init__(self):
        super().__init__(orientation='P', unit='mm', format=(PDF_WIDTH, PDF_HEIGHT))
        self.set_auto_page_break(auto=False)
        self.load_fonts()
    
    def load_fonts(self):
        """تحميل الخطوط المطلوبة"""
        try:
            self.add_font('NotoSansArabic-Bold', '', NOTO_SANS_ARABIC_BOLD)
            self.add_font('NotoSansArabic-Regular', '', NOTO_SANS_ARABIC_REGULAR)
            
            try:
                self.add_font('TimesNRMTPro-Bold', '', TIMES_NR_MT_BOLD)
                self.add_font('TimesNRMTPro-Regular', '', TIMES_NR_MT_REGULAR)
                self.times_available = True
            except:
                self.times_available = False
                print("استخدام الخطوط المدمجة للنصوص الإنجليزية")
            
        except Exception as e:
            print(f"خطأ في تحميل الخطوط: {e}")
    
    def process_arabic_text(self, text):
        """معالجة النص العربي لعرضه بشكل صحيح"""
        if not text:
            return ""
        
        try:
            reshaped_text = arabic_reshaper.reshape(text)
            bidi_text = get_display(reshaped_text)
            return bidi_text
        except Exception as e:
            print(f"خطأ في معالجة النص العربي: {e}")
            return text
    
    def add_header_images(self):
        """إضافة الصور والشعارات في الرأس"""
        try:
            if os.path.exists(SEHA_LOGO):
                self.image(SEHA_LOGO, x=11, y=12, w=56, h=26)
            
            if os.path.exists(GEOMETRIC_SHAPE):
                self.image(GEOMETRIC_SHAPE, x=191, y=12, w=94, h=40)
            
            if os.path.exists(KINGDOM_TEXT):
                self.image(KINGDOM_TEXT, x=100, y=13, w=94, h=45)
                
        except Exception as e:
            print(f"خطأ في إضافة صور الرأس: {e}")
    
    def add_titles(self):
        """إضافة العناوين الرئيسية"""
        self.set_font('NotoSansArabic-Bold', size=22)
        self.set_text_color(48, 109, 181)
        self.set_xy(116, 57)
        arabic_title = self.process_arabic_text('تقرير إجازة مرضية')
        self.cell(68, 10, arabic_title, align='C')
        
        if self.times_available:
            self.set_font('TimesNRMTPro-Bold', size=18)
        else:
            self.set_font('Arial', 'B', size=18)
        self.set_text_color(44, 62, 119)
        self.set_xy(123, 69)
        self.cell(52, 7, 'Sick Leave Report', align='C')
    
    def generate_leave_id(self, id_number, admission_date, discharge_date):
        """توليد رمز الإجازة"""
        id_part = id_number[-4:] if len(id_number) >= 4 else id_number
        admission_nums = ''.join(filter(str.isdigit, admission_date))[-3:]
        discharge_nums = ''.join(filter(str.isdigit, discharge_date))[-4:]
        leave_number = (id_part + admission_nums + discharge_nums).ljust(11, '0')[:11]
        return f"PSL{leave_number}"
    
    def calculate_duration(self, admission_date_hijri, discharge_date_hijri, admission_date_gregorian, discharge_date_gregorian):
        """حساب مدة الإجازة"""
        try:
            admission_parts = admission_date_gregorian.split('-')
            discharge_parts = discharge_date_gregorian.split('-')
            
            if len(admission_parts) == 3 and len(discharge_parts) == 3:
                admission_dt = datetime(int(admission_parts[2]), int(admission_parts[1]), int(admission_parts[0]))
                discharge_dt = datetime(int(discharge_parts[2]), int(discharge_parts[1]), int(discharge_parts[0]))
                
                duration_days = (discharge_dt - admission_dt).days + 1
                duration_ar = f"{duration_days} يوم ({admission_date_hijri} إلى {discharge_date_hijri})"
                day_word = "day" if duration_days == 1 else "days"
                duration_en = f"{duration_days} {day_word} ({admission_date_gregorian} to {discharge_date_gregorian})"
                return duration_ar, duration_en
            else:
                duration_ar = f"1 يوم ({admission_date_hijri} إلى {discharge_date_hijri})"
                duration_en = f"1 day ({admission_date_gregorian} to {discharge_date_gregorian})"
                return duration_ar, duration_en
                
        except Exception as e:
            print(f"خطأ في حساب المدة: {e}")
            duration_ar = f"1 يوم ({admission_date_hijri} إلى {discharge_date_hijri})"
            duration_en = f"1 day ({admission_date_gregorian} to {discharge_date_gregorian})"
            return duration_ar, duration_en
    
    def add_table(self, data):
        """إضافة الجدول الرئيسي"""
        table_x = 12.5
        table_y = 85
        col_widths = [58, 83, 83, 48]
        row_heights = [15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15]
        
        row_bg_colors = {
            1: (44, 62, 119),
            3: (247, 247, 247),
            5: (247, 247, 247),
            7: (247, 247, 247),
            9: (247, 247, 247),
        }
        
        leave_id = self.generate_leave_id(
            data.get('id_number', '1234567890'),
            data.get('admission_date_gregorian', '01-01-2025'),
            data.get('discharge_date_gregorian', '01-01-2025')
        )
        
        duration_ar, duration_en = self.calculate_duration(
            data.get('admission_date_hijri', '01-01-1446'),
            data.get('discharge_date_hijri', '01-01-1446'),
            data.get('admission_date_gregorian', '01-01-2025'),
            data.get('discharge_date_gregorian', '01-01-2025')
        )
        
        processed_data = {}
        for key, value in data.items():
            if key.endswith('_ar') and value:
                processed_data[key] = self.process_arabic_text(value)
            else:
                processed_data[key] = value
        
        duration_ar_processed = self.process_arabic_text(duration_ar)
        
        table_data = [
            ['Leave ID', leave_id, '', self.process_arabic_text('رمز الإجازة')],
            ['Leave Duration', duration_en, duration_ar_processed, self.process_arabic_text('مدة الإجازة')],
            ['Admission Date', processed_data.get('admission_date_gregorian', ''), processed_data.get('admission_date_hijri', ''), self.process_arabic_text('تاريخ الدخول')],
            ['Discharge Date', processed_data.get('discharge_date_gregorian', ''), processed_data.get('discharge_date_hijri', ''), self.process_arabic_text('تاريخ الخروج')],
            ['Issue Date', processed_data.get('issue_date_gregorian', ''), '', self.process_arabic_text('تاريخ إصدار التقرير')],
            ['Name', processed_data.get('patient_name_en', ''), processed_data.get('patient_name_ar', ''), self.process_arabic_text('الاسم')],
            ['National ID / Iqama', processed_data.get('id_number', ''), '', self.process_arabic_text('رقم الهوية / الإقامة')],
            ['Nationality', processed_data.get('nationality_en', ''), processed_data.get('nationality_ar', ''), self.process_arabic_text('الجنسية')],
            ['Employer', processed_data.get('employer_en', ''), processed_data.get('employer_ar', ''), self.process_arabic_text('جهة العمل')],
            ["Practitioner Name", processed_data.get("doctor_name_en", ""), processed_data.get("doctor_name_ar", ""), self.process_arabic_text("اسم الممارس")],
            ['Position', processed_data.get('position_en', ''), processed_data.get('position_ar', ''), self.process_arabic_text('المسمى الوظيفي')],
        ]
        
        current_y = table_y
        
        for row_idx, row_data in enumerate(table_data):
            current_x = table_x
            row_height = row_heights[row_idx]
            
            if row_idx in row_bg_colors:
                self.set_fill_color(*row_bg_colors[row_idx])
                fill = True
            else:
                fill = False
            
            for col_idx, cell_text in enumerate(row_data):
                col_width = col_widths[col_idx]
                
                if self.is_merged_cell(row_idx, col_idx):
                    current_x += col_width
                    continue
                
                actual_width = col_width
                if self.is_merge_start(row_idx, col_idx):
                    actual_width = col_widths[col_idx] + col_widths[col_idx + 1]
                
                self.set_draw_color(217, 217, 217)
                self.set_line_width(0.5)
                self.rect(current_x, current_y, actual_width, row_height, 'D' if not fill else 'DF')
                
                self.set_cell_font_and_color(row_idx, col_idx, cell_text)
                
                if cell_text:
                    self.set_xy(current_x, current_y)
                    align = self.get_cell_alignment(row_idx, col_idx)
                    self.cell(actual_width, row_height, cell_text, align=align)
                current_x += col_width
            
            current_y += row_height
        
        self.set_draw_color(217, 217, 217)
        self.set_line_width(0.5)
        self.line(152, 254, 152, 335)
    
    def is_merged_cell(self, row_idx, col_idx):
        if row_idx in [0, 4, 6] and col_idx == 2:
            return True
        return False
    
    def is_merge_start(self, row_idx, col_idx):
        if row_idx in [0, 4, 6] and col_idx == 1:
            return True
        return False
    
    def set_cell_font_and_color(self, row_idx, col_idx, text):
        blue_color = (54, 111, 181)
        dark_blue = (44, 62, 119)
        white_color = (255, 255, 255)
        
        if row_idx == 1:
            if col_idx in [0, 3]:
                if col_idx == 0:
                    if self.times_available:
                        self.set_font('TimesNRMTPro-Bold', size=13)
                    else:
                        self.set_font('Arial', 'B', size=13)
                else:
                    self.set_font('NotoSansArabic-Bold', size=13)
                self.set_text_color(*white_color)
            else:
                if col_idx == 1:
                    if self.times_available:
                        self.set_font('TimesNRMTPro-Regular', size=13)
                    else:
                        self.set_font('Arial', '', size=13)
                else:
                    self.set_font('NotoSansArabic-Regular', size=13)
                self.set_text_color(*white_color)
        elif col_idx == 0:
            if self.times_available:
                self.set_font('TimesNRMTPro-Bold', size=13)
            else:
                self.set_font('Arial', 'B', size=13)
            self.set_text_color(*blue_color)
        elif col_idx == 1:
            font_size = 11 if row_idx == 5 else (11 if row_idx in [7, 9] else 13)
            if self.times_available:
                self.set_font('TimesNRMTPro-Regular', size=font_size)
            else:
                self.set_font('Arial', '', size=font_size)
            self.set_text_color(*dark_blue)
        elif col_idx == 2:
            self.set_font('NotoSansArabic-Regular', size=13)
            self.set_text_color(*dark_blue)
        elif col_idx == 3:
            self.set_font('NotoSansArabic-Bold', size=13)
            self.set_text_color(*blue_color)
    
    def get_cell_alignment(self, row_idx, col_idx):
        if row_idx in [0, 4, 6] and col_idx == 1:
            return 'C'
        else:
            return 'C'
    
    def add_footer_elements(self, data):
        """إضافة عناصر التذييل"""
        try:
            qr_data = f"{data.get('id_number', '')} - {self.generate_leave_id(data.get('id_number', ''), data.get('admission_date_gregorian', ''), data.get('discharge_date_gregorian', ''))} - {data.get('issue_date_gregorian', '')}"
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(QR_URL)
            qr.make(fit=True)
            
            qr_img = qr.make_image(fill_color="black", back_color="white")
            qr_path = os.path.join(OUTPUT_DIR, "temp_qr.png")
            qr_img.save(qr_path)
            
            self.image(qr_path, x=60, y=265, w=42, h=40)
            
            self.set_font('NotoSansArabic-Bold', size=10)
            self.set_text_color(0, 0, 0)
            self.set_xy(45, 308)
            line1_text = self.process_arabic_text('للتحقق من بيانات التقرير يرجى التأكد من زيارة موقع منصة صحة')
            self.cell(72, 6, line1_text, align='C')

            self.set_xy(45, 314)
            line2_text = self.process_arabic_text('الرسمي')
            self.cell(72, 6, line2_text, align='C')

            if self.times_available:
                self.set_font('TimesNRMTPro-Bold', size=9)
            else:
                self.set_font('Arial', 'B', size=9)
            self.set_text_color(0, 0, 0)
            self.set_xy(45, 320)
            line3_text = "To check the report please visit Seha's offical website"
            self.cell(72, 6, line3_text, align='C')

            if self.times_available:
                self.set_font('TimesNRMTPro-Regular', size=9)
            else:
                self.set_font('Arial', '', size=9)
            self.set_text_color(0, 0, 255)
            self.set_xy(45, 326)
            self.cell(72, 6, QR_URL, align='C', link=QR_URL)
            
            self.set_draw_color(0, 0, 255)
            self.set_line_width(0.1)
            link_start_x = 45 + (72 - self.get_string_width(QR_URL)) / 2
            link_end_x = link_start_x + self.get_string_width(QR_URL)
            self.line(link_start_x, 330, link_end_x, 330)
            
            if os.path.exists(qr_path):
                os.remove(qr_path)
            
            custom_logo = data.get('custom_logo')
            if custom_logo and os.path.exists(custom_logo):
                self.image(custom_logo, x=203, y=266, w=43, h=42)
            elif os.path.exists(HOSPITAL_LOGO):
                self.image(HOSPITAL_LOGO, x=203, y=266, w=43, h=42)
            
            hospital_name_ar = data.get('hospital_name_ar', 'مجمع عائلتي الطبي')
            hospital_name_en = data.get('hospital_name_en', 'My Family Medical Center')
            
            self.set_font('NotoSansArabic-Bold', size=12)
            self.set_text_color(0, 0, 0)
            self.set_xy(188, 309)
            processed_hospital_name = self.process_arabic_text(hospital_name_ar)
            self.cell(67, 10, processed_hospital_name, align='C')
            
            if self.times_available:
                self.set_font('TimesNRMTPro-Bold', size=12)
            else:
                self.set_font('Arial', 'B', size=12)
            self.set_text_color(0, 0, 0)
            self.set_xy(188, 320)
            self.cell(67, 10, hospital_name_en, align='C')
            
            if os.path.exists(HEALTH_INFO_CENTER_LOGO):
                self.image(HEALTH_INFO_CENTER_LOGO, x=231, y=336, w=54, h=26)
            
            current_time = data.get('time', '6:23 AM')
            current_date = datetime.now().strftime('%A, %d %B %Y')
            
            if self.times_available:
                self.set_font('TimesNRMTPro-Bold', size=12)
            else:
                self.set_font('Arial', 'B', size=12)
            self.set_text_color(0, 0, 0)
            self.set_xy(11, 339)
            self.cell(20, 6, current_time, align='L')
            
            self.set_xy(11, 347)
            self.cell(47, 6, current_date, align='L')
            
        except Exception as e:
            print(f"خطأ في إضافة عناصر التذييل: {e}")

def generate_sick_leave_pdf(data, user_id):
    """توليد تقرير الإجازة المرضية"""
    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        pdf = SickLeavePDF()
        pdf.add_page()
        
        pdf.add_header_images()
        pdf.add_titles()
        pdf.add_table(data)
        pdf.add_footer_elements(data)
        
        id_number = data.get('id_number', 'UNKNOWN')
        issue_date = data.get('issue_date_gregorian', datetime.now().strftime('%d-%m-%Y'))
        filename = f"Sick Leave{id_number}_{issue_date.replace('-', '')}.pdf"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        pdf.output(filepath)
        
        return filepath
        
    except Exception as e:
        print(f"خطأ في توليد PDF: {e}")
        raise e
