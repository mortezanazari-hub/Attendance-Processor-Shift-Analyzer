# -*- coding: utf-8 -*-
"""
MAIN_PROCESSOR: File-e asli-ye ejra-ye barname.
Hamahang kardan-e tanzimat, logic, khandan-e file va zakhire-ye khoruji.
"""

import pandas as pd
import sys
import os
import tkinter as tk
from tkinter import filedialog
from datetime import timedelta
import xlsxwriter

# Import kardan-e settings va logic
from settings import CUTOFF_HOUR, DEVICE_MAP_COLUMN_NAME, DATETIME_COLUMN_NAME, \
                     ODOO_ID_COLUMN_NAME, SHIFT_MODEL_COLUMN_NAME, EMPLOYEE_MAP_FILE, \
                     INPUT_FILE_EXTENSION
from shift_logic import convert_shamsi_to_gregorian, process_day_records_sequentially


# ------------------ MAIN ------------------
if __name__ == '__main__':
    # ... [Marahale 0 va 1 ghabl az Marhale 2 bedun-e taghir] ...
    # (Entekhab-e Noe File, Entekhab-e File Vorudi, Entekhab-e Maskan-e Khoruji)

    print('=' * 50)
    print('>>> Lotfan noe-ye file voroodi ra entekhab konid:')
    print("    1. Format-e Ghadim (sotun 'Name' + Tarikh-e Miladi)")
    print("    2. Format-e Jadid (sotun 'EnNo' + Tarikh-e Shamsi)")
    choice = input('>>> Adad-e gozine ra vared konid (1 ya 2): ').strip()

    if choice == '1':
        input_id_column = 'Name'
        is_shamsi_date = False
        print('--- Format-e Qadim entekhab shod. ---')
    elif choice == '2':
        input_id_column = 'EnNo'
        is_shamsi_date = True
        print('--- Format-e Jadid (Tarikh-e Shamsi) entekhab shod. ---')
    else:
        print('\n!!! KHATA: Entekhab na-motabar. Barname payan yaft.')
        sys.exit(1)

    print('=' * 50)
    print('>>> Dar hale baz kardan-e panjere entekhab file...')
    root = tk.Tk()
    root.withdraw()
    input_file_path = filedialog.askopenfilename(
        title='Lotfan file ekhtiyar konid (attendance XLSX)',
        initialdir='.',
        filetypes=(("Excel files", INPUT_FILE_EXTENSION), ("All files", "*.*"))
    )

    if not input_file_path:
        print('\n!!! Hich file-i entekhab nashod. Barname payan yaft.')
        sys.exit(1)

    input_file_name = os.path.basename(input_file_path)
    print(f"--- File entekhab shod: '{input_file_name}' ---")

    print('>>> Dar hale baz kardan-e panjere entekhab makane zakhire...')
    output_file_path = filedialog.asksaveasfilename(
        title='Lotfan makane zakhire file khoruji ra entekhab konid',
        initialdir='.',
        defaultextension='.xlsx',
        filetypes=(("Excel files", "*.xlsx"), ("All files", "*.*")),
        initialfile=f"khoruji_{os.path.splitext(input_file_name)[0]}.xlsx"
    )

    if not output_file_path:
        print('\n!!! Hich makani baraye zakhire entekhab nashod. Barname payan yaft.')
        sys.exit(1)

    print(f"--- File khoruji zakhire mishavad dar: '{output_file_path}' ---")
    odoo_csv_path = os.path.join(os.path.dirname(output_file_path), f"odoo_attendance_{os.path.splitext(input_file_name)[0]}.csv")
    
    # ----------------------------------------------------
    # Marhale 1 Ghabl az Marhale 2: Khandan-e file voroodi
    # ----------------------------------------------------
    try:
        print('\n>>> Marhale 1: Khandan-e file voroodi...')
        # Khandan-e file Excel voroodi.
        df = pd.read_excel(input_file_path)
        if input_id_column not in df.columns or DATETIME_COLUMN_NAME not in df.columns:
            print(f"\n!!! KHATA: Sotun-haye required ('{input_id_column}' ya '{DATETIME_COLUMN_NAME}') dar file voroodi vojood nadarad.")
            sys.exit(1)

        # ----------------------------------------------------
        # Marhale 2: Khandan-e file employee_map (Taghir dar in bakhsh)
        # ----------------------------------------------------
        print('>>> Marhale 2: Khandan-e file employee_map...')
        
        # Check kardan va khandan-e file employee map.
        employee_map_path = EMPLOYEE_MAP_FILE
        if not os.path.exists(employee_map_path):
            print(f"    - WARNING: File '{EMPLOYEE_MAP_FILE}' be soorat-e pishfarz peyda nashod.")
            print("    - Dar hale baz kardan-e panjere entekhab file...")
            
            # Baz kardan-e panjere baraye entekhab-e employee_map
            employee_map_path = filedialog.askopenfilename(
                title='Lotfan file employee_map.xlsx ro entekhab konid',
                initialdir='.',
                filetypes=(("Excel files", "*.xlsx"), ("All files", "*.*"))
            )
            
            if not employee_map_path:
                print('\n!!! KHATA: Hich file employee_map-i entekhab nashod. Barname payan yaft.')
                sys.exit(1)
            
            print(f"    - File employee_map entekhab shod: '{os.path.basename(employee_map_path)}'")


        employee_map = pd.read_excel(employee_map_path, dtype=str)
        required_cols = {DEVICE_MAP_COLUMN_NAME, ODOO_ID_COLUMN_NAME, SHIFT_MODEL_COLUMN_NAME}
        if not required_cols.issubset(set(employee_map.columns)):
            print(f"\n!!! KHATA: File employee_map bayad in 3 sotun ro dashte bashe: {', '.join(required_cols)}")
            sys.exit(1)

        employee_map[DEVICE_MAP_COLUMN_NAME] = employee_map[DEVICE_MAP_COLUMN_NAME].astype(str)
        employee_map_index = employee_map.set_index(DEVICE_MAP_COLUMN_NAME)
        # Mapping-e device_id be odoo_id va shift_model.
        odoo_map = employee_map_index[ODOO_ID_COLUMN_NAME].to_dict()
        shift_map = employee_map_index[SHIFT_MODEL_COLUMN_NAME].to_dict()

        print('>>> Marhale 3: Tabdil-e zaman va mohasebe ruz-e kari...')
        # ... [Baqie-ye manategh-e Marhale 3, 4, 5, 6 va 7 bedun-e taghir] ...

    # ... [Baqie-ye code marbut be Marhale 3 ta payan barname dar zakhire sazi] ...

        # Tabdil tarikh-e jalali be miladi dar soorat-e lzuum.
        if is_shamsi_date:
            print('    - Converting Shamsi -> Gregorian ...')
            df['timestamp'] = df[DATETIME_COLUMN_NAME].astype(str).apply(convert_shamsi_to_gregorian)
        else:
            print('    - Parsing Gregorian datetimes ...')
            df['timestamp'] = pd.to_datetime(df[DATETIME_COLUMN_NAME], errors='coerce')

        df = df.dropna(subset=['timestamp'])
        # Mohasebe logical_date baraye shenasaei-ye shift-haye shabane.
        df['logical_date'] = df['timestamp'].apply(lambda ts: (ts - timedelta(hours=CUTOFF_HOUR)).date() if pd.notnull(ts) else None)

        print(">>> Marhale 4: Mapping by device_id to get odoo_id and shift_model ...")
        
        if DEVICE_MAP_COLUMN_NAME not in df.columns:
            print(f"    - Warning: '{DEVICE_MAP_COLUMN_NAME}' not found in input. Using '{input_id_column}' as device key.")
            df[DEVICE_MAP_COLUMN_NAME] = df[input_id_column].astype(str)
        else:
            df[DEVICE_MAP_COLUMN_NAME] = df[DEVICE_MAP_COLUMN_NAME].astype(str)

        df['employee_id'] = df[DEVICE_MAP_COLUMN_NAME].map(odoo_map)
        df['shift_model'] = df[DEVICE_MAP_COLUMN_NAME].map(shift_map)

        print('>>> Marhale 5: Hazf-e data haye namotabar ...')
        before_count = len(df)
        df.dropna(subset=['timestamp', 'logical_date', 'employee_id', 'shift_model'], inplace=True)
        after_count = len(df)
        print(f"    - Records before: {before_count}, after dropping invalid: {after_count}")

        print('>>> Marhale 6: Mohasebe zaman-e vorud va khoruj ...')
        df_clean = df.sort_values(by=[DEVICE_MAP_COLUMN_NAME, 'timestamp'])

        all_results = {'valid': [], 'incomplete': []}
        all_odoo_records = []

        # Group kardan data bar asase device_id va logical_date
        grouped = df_clean.groupby([DEVICE_MAP_COLUMN_NAME, 'logical_date'])
        for (device_id, logical_date), group in grouped:
            employee_id = group['employee_id'].iloc[0]
            shift_model_name = group['shift_model'].iloc[0]

            day_records = group['timestamp'].tolist()
            
            # Ferestad-e process be function-e dakhel-e shift_logic
            day_results = process_day_records_sequentially(employee_id, shift_model_name, day_records, logical_date)
            all_results['valid'].extend(day_results.get('valid', []))
            all_results['incomplete'].extend(day_results.get('incomplete', []))
            all_odoo_records.extend(day_results.get('odoo_export', []))


        valid_attendance_df = pd.DataFrame(all_results['valid'])
        incomplete_attendance_df = pd.DataFrame(all_results['incomplete'])
        odoo_df = pd.DataFrame(all_odoo_records)

        all_dfs = []
        if not valid_attendance_df.empty:
            all_dfs.append(valid_attendance_df)
        if not incomplete_attendance_df.empty:
            all_dfs.append(incomplete_attendance_df)

        if all_dfs:
            final_df = pd.concat(all_dfs, ignore_index=True)
            
            # Sotun haye nahaee
            cols = ['شناسه کارمند', 'نوع رکورد', 'تاریخ میلادی', 'تاریخ جلالی', 'نام روز', 'مدل شیفت',
                    'زمان ورود', 'زمان خروج', 'مدت زمان (ساعت)', 'ساعات استاندارد',
                    'تأخیر (ساعت)', 'تعجیل (ساعت)', 'خروج زود (ساعت)', 
                    'ساعات مرخصی ساعتی', 'توضیحات مرخصی ساعتی',
                    'اضافه کاری', 'شیفت تشخیص داده شده', 'اطمینان تشخیص']
            
            final_df = final_df.reindex(columns=cols).fillna('')


            print('>>> Marhale 7: Zakhire kardan-e natayej dar file Excel ba table va sub-sheet ha...')
            
            writer = pd.ExcelWriter(output_file_path, engine='xlsxwriter')
            
            # 1. Zakhire kardan-e Worksheet-e asli (Gozareh Koll)
            sheet_name_main = 'گزارش حضور و غیاب'
            final_df.to_excel(writer, sheet_name=sheet_name_main, index=False)
            
            # Table kardan-e sheet-e asli
            worksheet_main = writer.sheets[sheet_name_main]
            (max_row, max_col) = final_df.shape
            worksheet_main.add_table(0, 0, max_row, max_col - 1, {
                'name': 'AllAttendanceTable',
                'columns': [{'header': col} for col in final_df.columns]
            })

            # 2. Zakhire kardan-e Sub-Sheet ha baraye har karmand
            unique_employees = final_df['شناسه کارمند'].unique()
            print(f"    - Dar hale sakhtan {len(unique_employees)} sub-sheet...")
            
            for employee_id in unique_employees:
                employee_df = final_df[final_df['شناسه کارمند'] == employee_id].copy()
                
                sheet_name_employee = f"کارمند {employee_id}"[:31] 
                
                employee_df.to_excel(writer, sheet_name=sheet_name_employee, index=False)
                
                if not employee_df.empty:
                    worksheet_employee = writer.sheets[sheet_name_employee]
                    (max_emp_row, max_emp_col) = employee_df.shape
                    
                    worksheet_employee.add_table(0, 0, max_emp_row, max_emp_col - 1, {
                        'name': f'Table_{employee_id}',
                        'columns': [{'header': col} for col in employee_df.columns]
                    })
                    
            
            writer.close()
            
            print(f"*** MOVAFFAGH: File '{output_file_path}' be soorat-e yek jadval-e ghabel-e filter zakhire shod (ba sub-sheet)! ***")

            # Zakhire kardan baraye Odoo (faghat record haye valid)
            if not odoo_df.empty:
                odoo_df.to_csv(odoo_csv_path, index=False)
                print(f"*** MOVAFFAGH: CSV '{odoo_csv_path}' ba sotun-haye English zakhire shod! ***)")
        else:
            print('\n!!! HICHDADE: Hich record-e sahih peyda nashod.')

    except Exception as e:
        print(f"\n!!! KHATA: Yek moshkel-e koli pish amad: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    print('=' * 50)
    print('>>> Payan-e ejra-ye barname.')
    print('=' * 50)