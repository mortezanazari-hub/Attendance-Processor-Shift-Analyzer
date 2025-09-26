# -*- coding: utf-8 -*-
"""
SETTINGS: Tamame tanzimat-e ghabl-e ejra, moshahede-ye sotunha, zarayeb,
va moshakhasat-e shift-ha dar in file zakhire mishavad.
"""
from datetime import time as py_time

# Esme sotun-e zaman dar file-e voroodi.
DATETIME_COLUMN_NAME = 'DateTime'
# Esme sotun-e device_id dar file-e voroodi va employee_map.
DEVICE_MAP_COLUMN_NAME = 'device_id'
# Esme sotun-e odoo_id dar employee_map.
ODOO_ID_COLUMN_NAME = 'odoo_id'
# Esme sotun-e shift_model dar employee_map.
SHIFT_MODEL_COLUMN_NAME = 'shift_model'
# Esme file-e employee_map ke shift-e karbarha ro moshakhas mikone.
EMPLOYEE_MAP_FILE = 'employee_map.xlsx'

# Format-e file-e voroodi (dar main_processor estefade mishavad).
INPUT_FILE_EXTENSION = '*.xlsx'

# Bishtarin moddat-e shift-e momken (baraye hazf-e etela'at-e gheyre ghabul).
MAX_SHIFT_DURATION = 16
# Zarib-e mohasebe-ye ezafe kari dar rooz-e ta'til.
OVERTIME_FACTOR_HOLIDAY = 1.5
# Zarib-e mohasebe-ye ezafe kari dar rooz-e normal.
OVERTIME_FACTOR_NORMAL = 1.0
# Minimum fasel-e bein-e do record baraye inke be onvane "morakhasi-ye sa'ati" shenakhte beshe.
MIN_LEAVE_GAP = 0.5
# Sa'at-e cutoff baraye moshakhas kardan-e logical_date (masalan, shabkari ha).
CUTOFF_HOUR = 5

# Mapping baraye tabdil esm haye shift az Finglish ya English be Farsi (baraye khoruji)
SHIFT_NAME_MAP = {
    'sobh_normal': 'صبح',
    'sobh_half': 'صبح',
    'asr': 'عصر',
    'shab': 'شب',
    'long_day': 'شیفت طولانی',
    'custom_early': 'شیفت زود',
    'custom_late': 'شیفت دیر',
    'روز تعطیل': 'روز تعطیل',
    'Sobh': 'صبح',
    'Asr': 'عصر',
    'Shab': 'شب',
    'single_friday_off': 'شیفت ثابت',
    'single_saturday_off': 'شیفت ثابت',
    'long_shift': 'شیفت طولانی',
    'auto_detect': 'تشخیص خودکار'
}

# ------------------ ALL POSSIBLE SHIFTS (Hamzaman dar shift_logic ham niaz hast) ------------------
ALL_POSSIBLE_SHIFTS = {
    'sobh_normal': {'start': py_time(7, 30), 'end': py_time(16, 0), 'standard_hours': 8.5, 'type': 'normal', 'name': 'sobh_normal'},
    'sobh_half': {'start': py_time(7, 30), 'end': py_time(13, 0), 'standard_hours': 5.5, 'type': 'half', 'name': 'sobh_half'},
    'asr': {'start': py_time(15, 30), 'end': py_time(0, 0), 'standard_hours': 8.5, 'type': 'evening', 'name': 'asr'},
    'shab': {'start': py_time(23, 30), 'end': py_time(8, 0), 'standard_hours': 8.5, 'type': 'night', 'name': 'shab'},
    'long_day': {'start': py_time(6, 0), 'end': py_time(18, 0), 'standard_hours': 12.0, 'type': 'long', 'name': 'long_day'},
    'custom_early': {'start': py_time(6, 0), 'end': py_time(14, 30), 'standard_hours': 8.5, 'type': 'early', 'name': 'custom_early'},
    'custom_late': {'start': py_time(9, 0), 'end': py_time(17, 30), 'standard_hours': 8.5, 'type': 'late', 'name': 'custom_late'},
}

# Dictionary-e shift-ha ke faghat baraye 'auto_detect' estefade mishan.
AUTO_DETECT_SHIFTS = {
    'sobh_normal': ALL_POSSIBLE_SHIFTS['sobh_normal'],
    'asr': ALL_POSSIBLE_SHIFTS['asr'],
    'shab': ALL_POSSIBLE_SHIFTS['shab'],
}

# Modle-haye shift ke dar file employee_map tarif shode.
SHIFT_MODELS = {
    'single_friday_off': {
        'holiday': 4,
        'shifts_by_day': {
            5: {'start': py_time(7, 30), 'end': py_time(16, 0), 'standard_hours': 8.5},
            6: {'start': py_time(7, 30), 'end': py_time(16, 0), 'standard_hours': 8.5},
            0: {'start': py_time(7, 30), 'end': py_time(16, 0), 'standard_hours': 8.5},
            1: {'start': py_time(7, 30), 'end': py_time(16, 0), 'standard_hours': 8.5},
            2: {'start': py_time(7, 30), 'end': py_time(16, 0), 'standard_hours': 8.5},
            3: {'start': py_time(7, 30), 'end': py_time(13, 0), 'standard_hours': 5.5},
        }
    },
    'single_saturday_off': {
        'holiday': 5,
        'shifts_by_day': {
            6: {'start': py_time(7, 30), 'end': py_time(16, 0), 'standard_hours': 8.5},
            0: {'start': py_time(7, 30), 'end': py_time(16, 0), 'standard_hours': 8.5},
            1: {'start': py_time(7, 30), 'end': py_time(16, 0), 'standard_hours': 8.5},
            2: {'start': py_time(7, 30), 'end': py_time(16, 0), 'standard_hours': 8.5},
            3: {'start': py_time(7, 30), 'end': py_time(16, 0), 'standard_hours': 8.5},
            4: {'start': py_time(7, 30), 'end': py_time(13, 0), 'standard_hours': 5.5},
        }
    },
    'double_shift': {
        'holiday': 5,
        'is_rotational': True,
        'shifts': [
            {'name': 'Sobh', 'start': py_time(7, 30), 'end': py_time(16, 0), 'standard_hours': 8.5},
            {'name': 'Asr', 'start': py_time(15, 30), 'end': py_time(0, 0), 'standard_hours': 8.5}
        ]
    },
    'triple_shift': {
        'holiday': 5,
        'is_rotational': True,
        'shifts': [
            {'name': 'Sobh', 'start': py_time(7, 30), 'end': py_time(16, 0), 'standard_hours': 8.5},
            {'name': 'Asr', 'start': py_time(15, 30), 'end': py_time(0, 0), 'standard_hours': 8.5},
            {'name': 'Shab', 'start': py_time(23, 30), 'end': py_time(8, 0), 'standard_hours': 8.5}
        ]
    },
    'long_shift': {
        'holiday': 6,
        'shifts_by_day': {
            0: {'start': py_time(6, 0), 'end': py_time(18, 0), 'standard_hours': 12.0},
            1: {'start': py_time(6, 0), 'end': py_time(18, 0), 'standard_hours': 12.0},
            2: {'start': py_time(6, 0), 'end': py_time(18, 0), 'standard_hours': 12.0},
            3: {'start': py_time(6, 0), 'end': py_time(18, 0), 'standard_hours': 12.0},
            4: {'start': py_time(6, 0), 'end': py_time(18, 0), 'standard_hours': 12.0},
            5: {'start': py_time(6, 0), 'end': py_time(18, 0), 'standard_hours': 12.0},
        }
    },
    'auto_detect': {
        'holiday': None,
        'use_auto_detection': True
    }
}