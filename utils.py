import os 
import pandas as pd
from datetime import datetime
from colors import *
from config import (
    category_for_1024_or_1026A_gl_code,
    category_for_1020_gl_code,
    category_for_1021_gl_code,
    category_for_4006_gl_code,
    other_changes_components_when_skuad_or_all_remote_in_contracting_entity,
    other_changes_components_when_skuad_or_all_remote_NOT_in_contracting_entity
)
from currencies import currencies

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
        invoice_number = lst[2].split(" ")[2]
        # due_date = " ".join("".join(lst[2:5]).split(" ")[2:5])
        # invoice_period = "".join(lst[4:7]).split(" ")[4:7][-1] + "".join(lst[4:7]).split(" ")[4:7][0]
        A=lst[4].split(" ")
        A.remove("") if "" in A else None
        A.remove("-") if "-" in A else None
        A.remove("\x00") if "\x00" in A else None
        invoice_period = A[-1] + A[0]
        invoice_datetime_obj = datetime.strptime(invoice_date, "%b %d %Y")
        # due_date_datetime_obj = datetime.strptime(due_date, "%b %d %Y")
    except Exception as e:
        print_bold_red(f"Unable to fetch invoice date and invoice due date: {e}")
    else:
        return invoice_datetime_obj.strftime("%d-%m-%y"), invoice_number, invoice_period

def get_currency(lst):
    currency = ""
    try:
        for l in lst[4:]:
            for cur in currencies:
                if l.find(cur) >= 0:
                    return cur
        if currency == "":
            raise Exception
    except Exception as e:
        print_bold_red(f"Unable to fetch Currency : {e}")
    
def get_address(page):
    try:
        data = page.search("Billing To")[0]
        x0 = data['x0']
        top = data['top']
        x1 = page.search("Amount")[0]['x1'] - 10
        bottom = page.search("Overall Summary")[0]['top'] - 10
        bounding_box = (x0, top, x1, bottom)
        txt = page.crop(bounding_box).extract_text()
        lst = txt.split("\n")
        customer_name = lst[1]
        address_line1 = lst[2]
        address_line2 = ""
        if len(lst) == 4:
            address_line2 = lst[3]
        return customer_name, address_line1, address_line2
    except Exception as e:
        print_bold_red(f"Unable to fetch Address and Customer name : {e}")

def get_due_date(page):
    try:
        data = page.search("Total Due Due by")[0]
        x0 = data['x0']
        top = data['top']
        x1 = page.width
        bottom = data['bottom'] + 100
        bounding_box = (x0, top, x1, bottom)
        txt = page.crop(bounding_box).extract_text()
        lst = txt.split("\n")
        if lst[0].endswith("2023" or "2024"):
            due_date_str = lst[0].replace("Total Due Due by ", "").replace(",","").replace(" ","")
        else:
            due_date_str = lst[0].replace("Total Due Due by ", "").replace(",","").replace(" ","") + lst[1]
        due_date_obj = datetime.strptime(due_date_str, "%b%d%Y")
        total_due = lst[-1].split(" ")[-1]            
    except Exception as e:
        print_bold_red(f"Unable to fetch Due Date/Total Due: {e}")
    else:
        return due_date_obj.strftime("%d-%m-%y"), total_due
    
def get_total_tax(page):
    try:
        data = page.search("Invoice Number")[0]
        x0 = data['x0']
        top = data['top']
        x1 = data['x1']
        bottom = data['bottom'] + 80
        bounding_box = (x0, top, x1, bottom)
        txt = page.crop(bounding_box).extract_text()
        lst = txt.split("\n")
        total_tax= lst[-1].split(" ")[-1]
    except Exception as e:
        print_bold_red(f"Unable to fetch Total Tax: {e}")
    else:
        return total_tax
def get_customer_name(lst, currency):
    try:
        customer_name = ""
        for index, l in enumerate(lst):
            if l.startswith("Billing To Customer Billing Address"):
                customer_name = lst[index+1]
                if customer_name.startswith(currency):
                    customer_name = lst[index+2]
                break
        if customer_name == "":
            raise Exception
            
    except Exception as e:
        print_bold_red(f"Unable to fetch Customer name : {e}")
    else:
        return customer_name

def get_team_summary(INVOICE_BREAKDOWN_DIR, file):
    try:
        excel = f"Invoice Breakdown - {file[:len(file)-4]}.xlsx"
        file_path = os.path.join(INVOICE_BREAKDOWN_DIR, excel)
        xls = pd.ExcelFile(file_path)
        sheet_to_df_map = {}
        if xls.sheet_names:
            for sheet_name in xls.sheet_names:
                sheet_to_df_map[sheet_name] = xls.parse(sheet_name)
            return sheet_to_df_map    
        else:
            print_bold_red(f"Unable to fetch team summary for sheet: {excel}")
            return None
    except Exception as e:
        print_bold_red(f"Unable to fetch team summary: {e}")
        return None

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

def get_lob_file_df(LOB_FILE_DIR):
    files = get_files(LOB_FILE_DIR)
    files_list = list(files)
    if len(files_list) > 1:
        print_bold_red("More than one LOB file present in LOB File Folder. Picking up 1st LOB file for further processing...")
    if len(files_list) == 0:
        print_bold_red("No LOB file found.")
        return None
    file = os.path.join(LOB_FILE_DIR,files_list[0])
    df = pd.read_csv(file)
    return df

def get_gl_code(category, component, contracting_entity):
    try:
        gl_code = ""
        if category in category_for_1024_or_1026A_gl_code:
            if ("skuad" in contracting_entity.lower() or "all remote" in contracting_entity.lower()):
                gl_code = "1024"
            else:
                gl_code = "1026A"
        
        if category in category_for_1020_gl_code:
            gl_code = "1020"

        if category in category_for_1021_gl_code:
            gl_code = "1021"

        if category in ["Other Charges"]:
            if ("skuad" in contracting_entity.lower() or "all remote" in contracting_entity.lower()):
                values_list = list(other_changes_components_when_skuad_or_all_remote_in_contracting_entity.values())
                key_list = list(other_changes_components_when_skuad_or_all_remote_in_contracting_entity.keys())
                for i in range(len(values_list)):
                    if component in values_list[i]:
                        gl_code = key_list[i]
                        break
            else:
                values_list = list(other_changes_components_when_skuad_or_all_remote_NOT_in_contracting_entity.values())
                key_list = list(other_changes_components_when_skuad_or_all_remote_NOT_in_contracting_entity.keys())
                for i in range(len(values_list)):
                    if component in values_list[i]:
                        gl_code = key_list[i]
                        break
        
        if category in category_for_4006_gl_code:
            gl_code = "4006"
    except Exception as e:
        print_bold_red(f"Error occured while fetching the gl code: {e}")
        return ""
    else:
        return gl_code
        
def get_tax_type(tax_percent, gl_code):
    tax_type = ""
    if tax_percent == 8:
        tax_type = "Standard-Rated Supplies"
    if tax_percent == 0:
        tax_type = "Zero-Rated Supplies"
    if tax_percent == 7:
        tax_type = "2022 Standard-Rated Supplies"
    if gl_code == "4006":
        tax_type = "No Tax"
        tax_percent = 0
    return tax_type, tax_percent

def generate_data(customer_name, address_line_1, address_line_2, invoice_number, invoice_date, due_date, total_due, country, name, column, value, contracting_entity, currency, invoice_period, component_value, gl_code, lob, department, tax_percent, tax_type):
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
                "InventoryItemCode": "",
                "*Description": f"{country} : {name} : {column} : {component_value} : {value} : {contracting_entity} : {invoice_period}",
                "*Quantity": 1,
                "*UnitAmount": value,
                "Discount": "",
                "*AccountCode": gl_code,
                "*TaxType": tax_type,
                "TaxAmount": value * tax_percent / 100,
                "TrackingName1": "LOB", 
                "TrackingOption1": lob,
                "TrackingName2": "Departments",
                "TrackingOption2": department,
                "Currency": currency,
                "BrandingTheme": ""
            }
    
    return data