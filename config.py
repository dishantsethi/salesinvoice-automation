column_names = [
    "Gross Pay",
    "Reimbursements",
    "Employer Contributions - Social",
    "Employer Contributions - Health",
    "Employer Contributions - Others",
    "Employer Contributions - Unemployment",
    "Amortisations/Accruals",
    "Other Charges",
    "Skuad Fee",
    "Refunds",
    "Security Deposit"
]
header_list = [
    "*ContactName",
    "EmailAddress",
    "POAddressLine1",
    "POAddressLine2",
    "POAddressLine3",
    "POAddressLine4",
    "POCity",
    "PORegion",
    "POPostalCode",
    "POCountry",
    "*InvoiceNumber",
    "Reference",
    "*InvoiceDate",
    "*DueDate",
    "Total",
    "InventoryItemCode",
    "*Description",
    "*Quantity",
    "*UnitAmount",
    "Discount",
    "*AccountCode",
    "*TaxType",
    "TaxAmount",
    "TrackingName1", 
    "TrackingOption1",
    "TrackingName2",
    "TrackingOption2",
    "Currency",
    "BrandingTheme"
]

category_for_1024_or_1026A_gl_code = [
    "Gross Pay",
    "Employer Contributions - Social",
    "Employer Contributions - Health",
    "Employer Contributions - Others",
    "Employer Contributions - Unemployment",
    "Amortisations/Accruals"
]
category_for_1020_gl_code = [
    "Skuad Fee"
]
category_for_1021_gl_code = [
    "Reimbursements"
]
category_for_4006_gl_code = [
    "Refunds",
    "Security Deposit"
]
other_changes_components_when_skuad_or_all_remote_in_contracting_entity = {
    "1024": ["Insurance Fee","PF Admin Charges","PF Admin Fee"],
    "1020": ["Device Fee"],
    "1022": ["Talent Subscription Fee"],
    "1026A": ["Others"]
}
other_changes_components_when_skuad_or_all_remote_NOT_in_contracting_entity = {
    "1026A": ["Insurance Fee","PF Admin Charges","PF Admin Fee"],
    "1020": ["Device Fee"],
    "1022": ["Talent Subscription Fee"],
    "1026A": ["Others"]
}
