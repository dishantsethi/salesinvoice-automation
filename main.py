import pdfplumber
from config import (
    INVOICE_FILE_DIR,
    MAPPING_FILE_DIR,
    column_names,
    header_list,
    INVOICE_BREAKDOWN_DIR,
    SALES_INVOICE_DIR,
    LOB_FILE_DIR
)
import os
from utils import (
    get_files,
    get_invoice_and_due_date,
    get_total_due_and_customer_name_and_invoice_number,
    get_team_summary,
    get_mapping_file_df,
    generate_data,
    get_gl_code,
    get_lob_file_df,
    get_tax_type
)
import pandas as pd
from colors import *
import time
import numpy as np
from datetime import datetime

def start():
    for file in get_files(INVOICE_FILE_DIR):
        if file.endswith(".pdf"):
            print_bold_blue("----------------------------------------------------------------------------------")
            print_bold_warning(f"File name: {file}")
            tic = time.time()
            mapping_file_df = get_mapping_file_df(MAPPING_FILE_DIR)
            lob_file_df = get_lob_file_df(LOB_FILE_DIR)
            if mapping_file_df is None or lob_file_df is None:
                exit()
            file_path = os.path.join(INVOICE_FILE_DIR, file)
            with pdfplumber.open(file_path) as pdf:
                txt = pdf.pages[0].extract_text()
                lst = txt.split("\n")
                invoice_date, due_date, invoice_period = get_invoice_and_due_date(lst[2])
                total_due, customer_name, total_tax, address_line_1, address_line_2, currency, invoice_number = get_total_due_and_customer_name_and_invoice_number(lst)
                tax_percent = round(float(total_tax.replace(",","")) * 100 / (float(total_due.replace(",","")) - float(total_tax.replace(",",""))))
                print_bold_header(f"Invoice Number: {invoice_number}")
            team_summary = get_team_summary(INVOICE_BREAKDOWN_DIR, file)
            if team_summary is None:
                continue
            lob_row = lob_file_df[lob_file_df["Client Registered Name"].str.split().str.join(" ") == customer_name]
            lob = lob_row["LOB"].values
            department = lob_row["Department"].values
            if len(lob) == 0 or len(department) == 0:
                err = f"Unable to find Client '{customer_name}' in 'Client Registered Name' in LOB logic file"
                file_object = open(f'errors{file[:len(file)-4]}.txt', 'a')
                file_object.write(f'{datetime.now().strftime("%H:%M:%S")} - {err}\n')
                file_object.close()
                lob = [""]
                department = [""]
            for country in team_summary:
                df = team_summary[country]
                category_column = df["Category"]
                component_column = df["Component"]
                
                for index, column in enumerate(category_column):
                    if column is np.nan:
                        category_column[index] = category_column[index-1]

                for index, column in enumerate(category_column):
                    if column in column_names:
                        iloc = df.iloc[index]
                        component_value = component_column[index] if component_column[index] is not np.nan else ""
                        for name in list(iloc.keys())[2:]:
                            row = mapping_file_df[
                                (mapping_file_df["Work Country"] == country) &
                                (mapping_file_df["Employee Name"].str.split().str.join(" ") == " ".join(name.split()))
                                ]
                            contracting_entity = row["Contracting Entity"].values
                            if len(contracting_entity) == 0:
                                err = f"Unable to find name '{name}' in 'Employee Name' or '{country}' in 'Work Country' column of mapping sheet. Invoice File: {file}"
                                file_object = open(f'errors{file[:len(file)-4]}.txt', 'a')
                                file_object.write(f'{datetime.now().strftime("%H:%M:%S")} - {err}\n')
                                file_object.close()
                                contracting_entity = ["NONE"]
                            value = 0 if iloc[name] is np.nan else iloc[name].split(" ")[1]
                            gl_code = get_gl_code(column, component_value,contracting_entity[0])
                            tax_type, tax_percent = get_tax_type(tax_percent, gl_code)
                            data = generate_data(customer_name, address_line_1, address_line_2, invoice_number, invoice_date, due_date, total_due, country, name, column, value, contracting_entity[0], currency, invoice_period, component_value, gl_code, lob[0], department[0], tax_percent, tax_type)
                            dataframe = pd.DataFrame([data])
                            invoice_file_path = os.path.join(SALES_INVOICE_DIR, f"SalesInvoice{file[:len(file)-4]}.csv")
                            headers = False if os.path.isfile(invoice_file_path) else header_list
                            dataframe.to_csv(invoice_file_path, mode='a', index=False, header=headers)

            print_bold_header(f"Sales invoice file generated: SalesInvoice{file[:len(file)-4]}.csv")
            toc = time.time()
            print_bold_green(f"Time Take: {toc-tic} seconds")
            print_bold_blue("----------------------------------------------------------------------------------")

if __name__ == "__main__":
    start()
