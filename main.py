import pdfplumber
from config import (
    INVOICE_FILE_DIR,
    MAPPING_FILE_DIR,
    column_names,
    header_list,
    INVOICE_BREAKDOWN_DIR,
    SALES_INVOICE_DIR
)
import os
from utils import (
    get_files,
    get_invoice_and_due_date,
    get_total_due_and_customer_name,
    get_team_summary,
    get_mapping_file_df,
    generate_data
)
import pandas as pd
from colors import *
import time
import numpy as np

def start():
    for file in get_files(INVOICE_FILE_DIR):
        if file.endswith(".pdf"):
            print_bold_blue("----------------------------------------------------------------------------------")
            print_bold_warning(f"File name: {file}")
            tic = time.time()

            mapping_file_df = get_mapping_file_df(MAPPING_FILE_DIR)
            invoice_number = file[:len(file)-4].replace("_","/") 
            print_bold_header(f"Invoice Number: {invoice_number}")
            file_path = os.path.join(INVOICE_FILE_DIR, file)
            with pdfplumber.open(file_path) as pdf:
                txt = pdf.pages[0].extract_text()
                lst = txt.split("\n")
                invoice_date, due_date = get_invoice_and_due_date(lst[2])
                total_due, customer_name, total_tax, address_line_1, address_line_2 = get_total_due_and_customer_name(lst)
            team_summary = get_team_summary(INVOICE_BREAKDOWN_DIR, file)

            for country in team_summary:
                df = team_summary[country]
                category_column = df["Category"]
                for index, column in enumerate(category_column):
                    if column in column_names:
                        iloc = df.iloc[index]
                        
                        for name in list(iloc.keys())[2:]:
                            row = mapping_file_df[
                                (mapping_file_df["Work Country"] == country) &
                                (mapping_file_df["Employee Name"].str.split().str.join(" ") == " ".join(name.split()))
                                ]
                            contracting_entity = row["Contracting Entity"].values
                            if len(contracting_entity) == 0:
                                err = f"Unable to find name '{name}' in 'Employee Name' or '{country}' in 'Work Country' column of mapping sheet. Invoice File: {file}"
                                file_object = open(f'errors{file[:len(file)-4]}.txt', 'a')
                                file_object.write(f'{err}\n')
                                file_object.close()
                                contracting_entity = ["NONE"]
                            value = 0 if iloc[name] is np.nan else iloc[name].split(" ")[1]
                            data = generate_data(customer_name, address_line_1, address_line_2, invoice_number, invoice_date, due_date, total_due, total_tax, country, name, column, value, contracting_entity[0])
                            
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
