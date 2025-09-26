# -*- coding: utf-8 -*-
"""
SHIFT_LOGIC: Tamame function haye marboot be mohasebat-e zaman, tabdil-e tarikh,
va tashkhis-e shift dar in file gharar darand.
"""
import pandas as pd
from jdatetime import datetime as jdatetime
from datetime import datetime as py_datetime, timedelta, time as py_time

# Import kardan-e tanzimat az file settings.py
from settings import CUTOFF_HOUR, MIN_LEAVE_GAP, MAX_SHIFT_DURATION, \
                     OVERTIME_FACTOR_NORMAL, OVERTIME_FACTOR_HOLIDAY, \
                     SHIFT_MODELS, AUTO_DETECT_SHIFTS, SHIFT_NAME_MAP


def convert_shamsi_to_gregorian(shamsi_str):
    """
    In function string-e tarikh-e jalali ro be object-e datetime-e miladi tabdil mikone.
    """
    if pd.isna(shamsi_str):
        return None
    s = str(shamsi_str).strip()
    try:
        parts = s.split()
        date_part = parts[0]
        time_part = parts[1] if len(parts) > 1 else '00:00:00'
        ymd = date_part.split('/')
        if len(ymd) != 3:
            return None
        year, month, day = int(ymd[0]), int(ymd[1]), int(ymd[2])
        tp = time_part.split(':')
        hour = int(tp[0]) if len(tp) > 0 else 0
        minute = int(tp[1]) if len(tp) > 1 else 0
        second = int(tp[2]) if len(tp) > 2 else 0
        return jdatetime(year, month, day, hour, minute, second).togregorian()
    except Exception:
        return None

def format_hours_to_h_m(hours):
    """
    In function ye adad-e desimal (sa'at) ro migire va be format 'HH:MM' tabdil mikone.
    """
    if pd.isna(hours) or hours < 0:
        return ""
    total_minutes = int(round(hours * 60))
    h = total_minutes // 60
    m = total_minutes % 60
    return f"{h}:{m:02d}"

def calculate_time_difference(start_time, end_time):
    """
    Fasl-e zamani bein-e do object-e time ro be saat barmigardone.
    Shift-haye shabane (az ye rooz ta rooz-e bad) ro ham moshkeli nadare.
    """
    s = start_time.hour * 3600 + start_time.minute * 60 + getattr(start_time, 'second', 0)
    e = end_time.hour * 3600 + end_time.minute * 60 + getattr(end_time, 'second', 0)
    if e < s:
        e += 24 * 3600
    return (e - s) / 3600.0

def detect_best_shift(check_in_time, check_out_time, shifts_dict=AUTO_DETECT_SHIFTS):
    """
    In function baraye rooz hayi ke shift moshakhas nist, behtarin shift-e momken ro tashkhis mide.
    """
    if not check_in_time or not check_out_time:
        return None

    best = None
    min_dev = float('inf')
    actual_duration = calculate_time_difference(check_in_time, check_out_time)

    # ... [Kamel kardan-e manategh-e tashkhis-e shift, mesl-e code-e ghabli] ...
    sobh_start = py_time(7, 30)
    sobh_start_min = sobh_start.hour * 60 + sobh_start.minute
    actual_in_min = check_in_time.hour * 60 + check_in_time.minute
    in_window = abs(actual_in_min - sobh_start_min) <= 240

    priority_shift = None
    if in_window:
        priority_shift = 'sobh_normal'

    for key, info in shifts_dict.items():
        start_min = info['start'].hour * 60 + info['start'].minute
        end_min = info['end'].hour * 60 + info['end'].minute
        actual_out_min = check_out_time.hour * 60 + check_out_time.minute

        expected_checkout = 24 * 60 if (info['end'].hour == 0 and info['end'].minute == 0) else end_min

        if info['end'].hour < info['start'].hour:
            if actual_out_min < 12 * 60:
                actual_out_min += 24 * 60

        check_in_dev = abs(actual_in_min - start_min)
        check_out_dev = abs(actual_out_min - expected_checkout)

        time_dev = (check_in_dev * 0.7) + (check_out_dev * 0.3)

        expected_duration = info['standard_hours']
        duration_dev = abs(actual_duration - expected_duration)

        weighted_dev = (time_dev * 0.6) + (duration_dev * 60 * 0.4)

        if priority_shift == key:
            weighted_dev *= 0.8

        if weighted_dev < min_dev:
            min_dev = weighted_dev
            best = {
                'key': key,
                'info': info,
                'deviation': weighted_dev,
                'actual_duration': actual_duration
            }

    if best is None:
        return None

    confidence = max(0.0, 100.0 - min(100.0, best['deviation'] / 10.0))
    return {'info': best['info'], 'deviation': best['deviation'], 'confidence': confidence, 'actual_duration': best['actual_duration']}


def get_shift_for_day(shift_model, logical_date, check_in_time=None, check_out_time=None):
    """
    In function baraye yek rooz-e moshakhas, shift-e marboot be on rooz ro barmigardone.
    """
    weekday = logical_date.weekday()
    if shift_model.get('use_auto_detection', False):
        if check_in_time and check_out_time:
            detected = detect_best_shift(check_in_time, check_out_time, shifts_dict=AUTO_DETECT_SHIFTS)
            if detected:
                info = detected['info']
                return {
                    'start': info['start'],
                    'end': info['end'],
                    'standard_hours': info['standard_hours'],
                    'detected_shift': info.get('name', detected.get('key', 'auto')),
                    'detection_confidence': detected.get('confidence', 0.0)
                }
        return None

    if 'holiday' in shift_model and shift_model['holiday'] == weekday:
        return None

    if shift_model.get('is_rotational', False) and 'shifts' in shift_model:
        week_number = logical_date.isocalendar()[1]
        shifts = shift_model['shifts']
        idx = week_number % len(shifts) if len(shifts) > 0 else 0
        s = shifts[idx]
        return {'start': s['start'], 'end': s['end'], 'standard_hours': s['standard_hours'], 'name': s.get('name')}

    if 'shifts_by_day' in shift_model:
        s = shift_model['shifts_by_day'].get(weekday)
        if s:
            return {'start': s['start'], 'end': s['end'], 'standard_hours': s['standard_hours'], 'name': s.get('name')}

    return None

def calculate_delay(check_in_dt, shift_start_time):
    """
    In function mi'an-e ta'khir hangam-e vorood-e karmand ro mohasebe mikone.
    """
    if not check_in_dt or not shift_start_time:
        return 0
    check_in_time = check_in_dt.time()
    cis = check_in_time.hour * 3600 + check_in_time.minute * 60 + getattr(check_in_time, 'second', 0)
    ss = shift_start_time.hour * 3600 + shift_start_time.minute * 60 + getattr(shift_start_time, 'second', 0)
    if cis > ss:
        return (cis - ss) / 3600.0
    return 0

def calculate_early_arrival(check_in_dt, shift_start_time):
    """
    In function mi'an-e vorood-e zoodtar az zaman-e shoru-ye shift ro mohasebe mikone.
    """
    if not check_in_dt or not shift_start_time:
        return 0
    check_in_time = check_in_dt.time()
    cis = check_in_time.hour * 3600 + check_in_time.minute * 60 + getattr(check_in_time, 'second', 0)
    ss = shift_start_time.hour * 3600 + shift_start_time.minute * 60 + getattr(shift_start_time, 'second', 0)
    if cis < ss:
        return (ss - cis) / 3600.0
    return 0

def calculate_early_departure(check_out_dt, shift_start_time, shift_end_time):
    """
    In function mi'an-e khorooj-e zoodtar az zaman-e payan-e shift ro mohasebe mikone.
    Shift-haye shabane ro ham dar nazar migire.
    """
    if not check_out_dt or not shift_start_time or not shift_end_time:
        return 0
    co_time = check_out_dt.time()
    cos = co_time.hour * 3600 + co_time.minute * 60 + getattr(co_time, 'second', 0)
    ss = shift_start_time.hour * 3600 + shift_start_time.minute * 60 + getattr(shift_start_time, 'second', 0)
    es = shift_end_time.hour * 3600 + shift_end_time.minute * 60 + getattr(shift_end_time, 'second', 0)

    # Mohasebe baraye shift-haye shabane
    if es <= ss:
        es += 24 * 3600
        if cos < ss:
            cos += 24 * 3600

    if cos < es:
        return (es - cos) / 3600.0
    return 0

def process_day_records_sequentially(employee_id, shift_model_name, records, logical_date):
    """
    Record-haye yek karmand dar yek rooz ro be tartib process mikone va natije ro barmigardone.
    """
    result = {
        'valid': [],
        'incomplete': [],
        'odoo_export': []
    }

    if not records:
        return result

    model = SHIFT_MODELS.get(shift_model_name)
    if model is None:
        # [Manategh-e zakhire-ye record-e naqes - mesl-e code-e ghabli]
        jalali_date = jdatetime.fromgregorian(date=logical_date).strftime('%Y-%m-%d')
        day_names = ['دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنج‌شنبه', 'جمعه', 'شنبه', 'یکشنبه']
        day_name = day_names[logical_date.weekday()]
        result['incomplete'].append({
            'شناسه کارمند': employee_id,
            'تاریخ میلادی': logical_date,
            'تاریخ جلالی': jalali_date,
            'نام روز': day_name,
            'نوع رکورد': 'ناقص',
            'زمان ورود': '',
            'زمان خروج': '',
            'مدت زمان (ساعت)': 0,
            'نوع': 'invalid_shift_model'
        })
        return result

    jalali_date = jdatetime.fromgregorian(date=logical_date).strftime('%Y-%m-%d')
    day_names = ['دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنج‌شنبه', 'جمعه', 'شنبه', 'یکشنبه']
    day_name = day_names[logical_date.weekday()]

    pairs = []
    # Zoj kardan-e check-in va check-out
    for i in range(0, len(records), 2):
        check_in = records[i]
        check_out = records[i+1] if (i+1) < len(records) else None
        pairs.append({'check_in': check_in, 'check_out': check_out})

    # Mohasebe morakhasi sa'ati dar bein-e zoj ha
    total_hourly_leave = 0.0
    hourly_leave_details = []
    for i in range(len(pairs) - 1):
        if pairs[i]['check_out'] and pairs[i+1]['check_in']:
            leave_start = pairs[i]['check_out']
            leave_end = pairs[i+1]['check_in']
            leave_hours = (leave_end - leave_start).total_seconds() / 3600.0
            if leave_hours > MIN_LEAVE_GAP:
                total_hourly_leave += leave_hours
                hourly_leave_details.append(
                    f"{leave_start.strftime('%H:%M')} ta {leave_end.strftime('%H:%M')}"
                )
    
    hourly_leave_formatted = format_hours_to_h_m(total_hourly_leave)
    hourly_leave_info = f" ({', '.join(hourly_leave_details)})" if hourly_leave_details else ""


    for i, pair in enumerate(pairs):
        check_in = pair['check_in']
        check_out = pair['check_out']
        
        if not check_out:
            # [Manategh-e zakhire-ye record-e naqes - mesl-e code-e ghabli]
            result['incomplete'].append({
                'شناسه کارمند': employee_id,
                'تاریخ میلادی': logical_date,
                'تاریخ جلالی': jalali_date,
                'نام روز': day_name,
                'نوع رکورد': 'ناقص',
                'زمان ورود': check_in.strftime('%Y-%m-%d %H:%M:%S'),
                'زمان خروج': '',
                'مدت زمان (ساعت)': 0,
                'نوع': 'missing_exit'
            })
            continue

        duration_hours_float = (check_out - check_in).total_seconds() / 3600.0
        if duration_hours_float <= 0 or duration_hours_float > MAX_SHIFT_DURATION:
            continue

        duration_hours_formatted = format_hours_to_h_m(duration_hours_float)
        shift = get_shift_for_day(model, logical_date, check_in.time(), check_out.time())

        # [Mohasebat-e Jame-e shift, overtime, ta'khir, ta'jil - mesl-e code-e ghabli]
        detected_info_raw = None
        confidence = None
        start = None
        end = None
        standard_hours = 0

        if shift:
            start = shift.get('start')
            end = shift.get('end')
            standard_hours = shift.get('standard_hours', 0)
            if 'detected_shift' in shift:
                detected_info_raw = shift.get('detected_shift')
            elif 'name' in shift:
                detected_info_raw = shift.get('name')
            else:
                detected_info_raw = shift_model_name
            
            conf_val = shift.get('detection_confidence')
            try:
                confidence = float(conf_val) if conf_val is not None else None
            except Exception:
                confidence = None
        else:
            detected_info_raw = 'روز تعطیل'

        translated_shift_name = SHIFT_NAME_MAP.get(detected_info_raw, detected_info_raw)

        if standard_hours and standard_hours > 0:
            overtime = max(0.0, duration_hours_float - standard_hours) * OVERTIME_FACTOR_NORMAL
        else:
            overtime = duration_hours_float * OVERTIME_FACTOR_HOLIDAY
        
        overtime_formatted = format_hours_to_h_m(overtime)
        overtime_float = overtime

        delay_hours = calculate_delay(check_in, start) if start else 0
        early_arrival_hours = calculate_early_arrival(check_in, start) if start else 0
        early_departure_hours = calculate_early_departure(check_out, start, end) if start and end else 0
        
        delay_hours_formatted = format_hours_to_h_m(delay_hours)
        early_arrival_hours_formatted = format_hours_to_h_m(early_arrival_hours)
        early_departure_hours_formatted = format_hours_to_h_m(early_departure_hours)

        record = {
            'شناسه کارمند': employee_id,
            'تاریخ میلادی': logical_date,
            'تاریخ جلالی': jalali_date,
            'نام روز': day_name,
            'نوع رکورد': 'حضور معتبر',
            'زمان ورود': check_in.strftime('%Y-%m-%d %H:%M:%S'),
            'زمان خروج': check_out.strftime('%Y-%m-%d %H:%M:%S'),
            'مدت زمان (ساعت)': duration_hours_formatted, 
            'ساعات استاندارد': standard_hours,
            'اضافه کاری': overtime_formatted,
            'تأخیر (ساعت)': delay_hours_formatted,
            'تعجیل (ساعت)': early_arrival_hours_formatted,
            'خروج زود (ساعت)': early_departure_hours_formatted,
            'ساعات مرخصی ساعتی': hourly_leave_formatted,
            'مدل شیفت': shift_model_name,
            'شیفت تشخیص داده شده': translated_shift_name,
            'اطمینان تشخیص': f"{confidence:.1f}%" if confidence is not None else ""
        }
        
        if hourly_leave_info and i == len(pairs) - 1:
             record['توضیحات مرخصی ساعتی'] = hourly_leave_info
        else:
            record['توضیحات مرخصی ساعتی'] = ""
        
        result['valid'].append(record)
        
        odoo_record = {
            'employee_id': employee_id,
            'check_in': check_in.strftime('%Y-%m-%d %H:%M:%S'),
            'check_out': check_out.strftime('%Y-%m-%d %H:%M:%S'),
            'overtime': overtime_float
        }
        result['odoo_export'].append(odoo_record)

    return result