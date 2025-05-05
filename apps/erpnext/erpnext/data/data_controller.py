import frappe
from frappe import _
import json
from .import_model import (create_doctypes, read_csv_file_as_dict) 
from frappe.exceptions import ValidationError
from frappe.core.doctype.file.file import File

# ------------------------ RESET DATA ------------------------ #
@frappe.whitelist()
def reset_data(doctypes):
    if frappe.session.user != "Administrator":
        frappe.throw(_("Only Administrator can perform this action."))

    if isinstance(doctypes, str):
        doctypes = json.loads(doctypes)

    if not doctypes or not isinstance(doctypes, list):
        frappe.throw(_("Invalid doctype list."))

    deleted = []

    for doctype in doctypes:
        if frappe.get_meta(doctype, cached=True).issingle:
            continue  # skip singleton Doctypes
        try:
            frappe.db.delete(doctype)
            deleted.append(doctype)
        except Exception as e:
            frappe.log_error(f"Failed to delete {doctype}: {str(e)}")

    return {"message": "Done", "deleted": deleted}


# ------------------------ IMPORT DATA ------------------------ #
@frappe.whitelist(allow_guest=True)
def import_data():
    uploaded_suppliers = frappe.request.files.get('file2')
    uploaded_material = frappe.request.files.get('file1')
    uploaded_quotation = frappe.request.files.get('file3')

    if not uploaded_suppliers or not uploaded_material or not uploaded_quotation:
        frappe.throw("No file uploaded. Please include a file field named 'file'.")

    try:
        create_doctypes(
            read_csv_file_as_dict(uploaded_material),
            read_csv_file_as_dict(uploaded_suppliers),
            read_csv_file_as_dict(uploaded_quotation),
        )
        frappe.db.commit()

    except Exception as e:
        frappe.db.rollback()
        frappe.throw(f"Failed to process file: {e}")

    return "File imported successfully"