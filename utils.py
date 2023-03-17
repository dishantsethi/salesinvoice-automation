import os 
import pandas as pd
from datetime import datetime
from colors import *

def listdir_nohidden(dir):
    for f in os.listdir(dir):
        if not f.startswith('.'):
            yield f

def get_files(dir):
    return listdir_nohidden(dir)

def get_invoice_and_due_date(str):
    try:
        lst = str.split(",")
        invoice_date = " ".join("".join(lst[:3]).split(" ")[:3])
        due_date = " ".join("".join(lst[2:5]).split(" ")[2:5])
        invoice_period = "".join(lst[4:7]).split(" ")[4:7][-1] + "".join(lst[4:7]).split(" ")[4:7][0]
        invoice_datetime_obj = datetime.strptime(invoice_date, "%b %d %Y")
        due_date_datetime_obj = datetime.strptime(due_date, "%b %d %Y")
    except Exception as e:
        print_bold_red(f"Unable to fetch invoice date and invoice due date: {e}")
    else:
        return invoice_datetime_obj.strftime("%d-%m-%y"), due_date_datetime_obj.strftime("%d-%m-%y"), invoice_period

def get_total_due_and_customer_name(list):
    try:
        for index, l in enumerate(list):
            if l.endswith("Total Due"):
                total_due_list = list[index+1].split(" ")[-1:-3:-1]
                total_tax_list = list[index+1].split(" ")[-3:-5:-1]
            if l.endswith("Bill To"):
                customer_name = list[index+1]
                address_line_1 = list[index+2]
                address_line_2 = list[index+3]
    except Exception as e:
        print_bold_red(f"Unable to fetch Total Due/Total Tax/Cust Name/Address : {e}")
    else:
        return total_due_list[0], customer_name, total_tax_list[0], address_line_1, address_line_2, total_due_list[1]

def get_team_summary(INVOICE_BREAKDOWN_DIR, file):
    try:
        excel = f"Invoice Breakdown - {file[:len(file)-4]}.xlsx"
        file_path = os.path.join(INVOICE_BREAKDOWN_DIR, excel)
        xls = pd.ExcelFile(file_path)
        sheet_to_df_map = {}
        for sheet_name in xls.sheet_names:
            sheet_to_df_map[sheet_name] = xls.parse(sheet_name)
    except Exception as e:
        print_bold_red(f"Unable to fetch team summary: {e}")
        return None
    else:
        return sheet_to_df_map    

def get_mapping_file_df(MAPPING_FILE_DIR):
    files = get_files(MAPPING_FILE_DIR)
    files_list = list(files)
    if len(files_list) > 1:
        print_bold_red("More than one mapping file present in Mapping File Folder. Picking up 1st Mapping file for further processing...")
    if len(files_list) == 0:
        print_bold_red("No mapping file found.")
        return None
    file = os.path.join(MAPPING_FILE_DIR,files_list[0])
    df = pd.read_csv(file)
    return df

def generate_data(customer_name, address_line_1, address_line_2, invoice_number, invoice_date, due_date, total_due, total_tax, country, name, column, value, contracting_entity, currency, invoice_period):
    data = {
                "*ContactName": customer_name,
                "EmailAddress": "",
                "POAddressLine1": address_line_1,
                "POAddressLine2": address_line_2,
                "POAddressLine3": "",
                "POAddressLine4": "",
                "POCity": "",
                "PORegion": "",
                "POPostalCode": "",
                "POCountry": "",
                "*InvoiceNumber": invoice_number,
                "Reference": "",
                "*InvoiceDate": invoice_date,
                "*DueDate": due_date,
                "Total": total_due.replace(",", ""),
                "TaxTotal": total_tax.replace(",", ""),
                "InvoiceAmountPaid": 0,
                "InvoiceAmountDue": total_due.replace(",", ""),
                "InventoryItemCode": "",
                "*Description": f"{country} : {name} : {column} : {value} : {contracting_entity} : {invoice_period}",
                "*Quantity": "",
                "*UnitAmount": value,
                "Discount": "",
                "LineAmount": "",
                "*AccountCode": "",
                "*TaxType": "",
                "TaxAmount": "",
                "TrackingName1": "LOB", 
                "TrackingOption1": "Global Employment",
                "TrackingName2": "Departments",
                "TrackingOption2": "Platform-Compliance + Payments",
                "Currency": currency,
                "Type": "Sales Invoice",
                "Sent": "",
                "Status": ""
            }
    
    return data