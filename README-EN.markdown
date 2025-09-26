# 📚 Attendance Processor & Shift Analyzer

A powerful Python-based tool for processing raw attendance data (punch records) from time clock devices. It automatically detects work shifts, calculates detailed attendance metrics (e.g., delay, early departure, overtime), and generates comprehensive reports in Excel and Odoo-ready CSV formats.

---

## 🎯 Key Features

- **Modular & Configurable**: Organized into three modules (`settings.py`, `shift_logic.py`, `main_processor.py`) for easy management and extensibility.
- **Automatic Shift Detection**: Detects the best shift (Morning, Evening, Night) based on check-in/out times, ideal for flexible schedules.
- **Jalali & Gregorian Support**: Processes input files in **Jalali (Shamsi)** or **Gregorian** date formats.
- **Detailed Reporting**: Computes **Total Attendance Hours**, **Overtime**, **Delay**, **Early Arrival**, **Early Departure**, and **Hourly Leave** with precise time details.
- **Multi-Sheet Excel Output**: Generates a single Excel file with a **Master Report** (formatted with tables and filters) and individual **Sub-Sheets** for each employee.
- **Odoo-Ready CSV**: Produces a CSV file with standardized columns (`employee_id`, `check_in`, `check_out`, `overtime`) for direct import into ERP systems like **Odoo**.

---

## 💡 Input Data Flexibility and Compatibility

This tool is engineered for high flexibility and compatibility with output from various time clock devices.

- **Initial Data Source**: Initial development and successful testing were conducted using output from **ST-Face 122** and **ST-Face E512** devices by Elm o Sanat. Raw data from these devices (typically in text format) is converted to Excel before processing.
- **Zero Dependency**: There is no mandatory dependency on specific devices (e.g., Elm o Sanat) or ERP systems (e.g., Odoo).
- **Minimum Requirements**: The raw input file (after conversion to Excel) only needs to include the **User ID/Code registered on the device** and the **column containing the attendance record datetime**. All subsequent processing, shift categorization, and calculations are handled automatically by the tool.

---

## 🛠️ Prerequisites

Ensure **Python** is installed along with the following packages:

```bash
pip install pandas jdatetime xlsxwriter openpyxl tk
```

---

## 📂 Project Structure

The project directory should contain:

```
/attendance_processor/
├── main_processor.py       # Main execution logic and workflow
├── settings.py             # Constants, mappings, and shift models
├── shift_logic.py          # Helper functions, time calculations, and shift detection logic
└── employee_map.xlsx       # Employee mapping file (Required)
```

---

## ⚙️ Configuring `employee_map.xlsx`

This file is essential and must contain the following columns:

| Column (Header) | Description |
|-----------------|-------------|
| `device_id`     | Employee/card ID from the raw input file (e.g., `EnNo` or `Name`). |
| `odoo_id`       | Official employee code for the final output and Odoo CSV. |
| `shift_model`   | Shift model name (e.g., `single_friday_off`, `triple_shift`, `auto_detect`). |

### Supported Shift Models

| Shift Model            | Type         | Description                                      |
|------------------------|--------------|--------------------------------------------------|
| `single_friday_off`    | Fixed        | Fixed shift with Friday off (Thursday half-shift). |
| `single_saturday_off`  | Fixed        | Fixed shift with Saturday off (Thursday half-shift). |
| `double_shift`         | Rotational   | Two shifts (e.g., Morning/Evening), rotating weekly. |
| `triple_shift`         | Rotational   | Three shifts (Morning/Evening/Night), rotating weekly. |
| `long_shift`           | Long (12h)   | Fixed 12-hour shift model.                       |
| **`auto_detect`**      | Automatic    | Detects best shift (Morning/Evening/Night) based on times. |

---

## 🚀 How to Run and Customization

1. **Setup**: Place all Python files and `employee_map.xlsx` in the same directory.
2. **Execute**: Run the main script from your terminal:

   ```bash
   python main_processor.py
   ```

3. **Follow Prompts**:
   - **Input Date Type**: Select whether the raw file uses Jalali or Gregorian dates.
     - **Date Format Customization Tip**: If the raw input data format (e.g., default column names like `Name`/`EnNo` or date format) differs from the prompted options, edit the `main_processor.py` file. In the `if __name__ == '__main__':` block, adjust the variables for the user ID column (`input_id_column`) and datetime column (`DATETIME_COLUMN_NAME`) to match your input file.
   - **Select Raw File**: Choose the input attendance Excel file.
   - **Select Output Path**: Specify the path and name for the output Excel file.
   - **Select `employee_map`**: If `employee_map.xlsx` is not found, a file dialog will prompt manual selection.
4. **Output**: Two files (Excel and CSV) will be generated in the specified path, including a standardized CSV file compatible with **Odoo** for seamless ERP integration.

---

## 🔧 Technical Logic & Calculations

### 1. Logical Workday (`logical_date`)
To handle night shifts, a **CUTOFF_HOUR** (default **5:00 AM**) is used. Records before this hour are assigned to the previous day's "workday" for accurate night shift grouping.

### 2. Hourly Leave Calculation
- **Logic**: Identifies gaps between sequential check-out and check-in records for an employee on the same day.
- **Threshold**: Gaps exceeding **MIN_LEAVE_GAP** (default **0.5 hours/30 minutes**) are reported as **Hourly Leave**.

### 3. Attendance Metrics
| Metric            | Calculation Method                              |
|-------------------|------------------------------------------------|
| **Delay**         | `MAX(0, Check-in Time - Shift Start Time)`     |
| **Early Departure** | `MAX(0, Shift End Time - Check-out Time)`     |
| **Overtime**      | `MAX(0, Total Attendance Hours - Standard Shift Hours)` |

> **Note**: On non-shift days (e.g., weekly holidays), all attendance hours are counted as **Overtime**.

---

## 🌐 Language Support
This README combines both **English** and **Persian** documentation for broader accessibility. For detailed Persian documentation, refer to the original files.