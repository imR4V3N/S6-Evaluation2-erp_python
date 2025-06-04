import frappe
from frappe import _
import base64
from hrms.data.services.Service import Service
from hrms.data.services.insert import (
    setup_hrms_data,
    insert_employees,
    insert_salary_components,
    insert_salary_structures,
    insert_salary_assignments,
    insert_salary_slips
)
from hrms.data.dto.EmployeeDto import EmployeeDTO
from hrms.data.dto.SalaryDto import SalaryDTO
from hrms.data.dto.PayrollDto import PayrollDTO

@frappe.whitelist(allow_guest=False)
def import_csv(): 
    """
    API to import three CSV files for HRMS: file1(Employee), file2(Salary Component & Salary Structure), file3 (Salary Structure Assignement & Salary Slip).
    Endpoint: /api/method/hrms.data.import_controller.import_csv
    Method: POST
    Expects: JSON payload with base64-encoded CSV files.
    """
    # Permission checks
    for doctype in ["Employee", "Salary Structure", "Salary Slip", "Salary Component"]:
        if not frappe.has_permission(doctype, "create"):
            frappe.local.response["status"] = "error"
            frappe.local.response["message"] = _(f"You do not have permission to create {doctype} records.")
            return

    try:
        # Get JSON payload
        data = frappe.request.get_json()
        if not data:
            frappe.local.response["status"] = "error"
            frappe.local.response["message"] = _("No data provided in the request.")
            return

        csv_configs = [
            {"file_key": "file1", "dto_class": EmployeeDTO},
            {"file_key": "file2", "dto_class": SalaryDTO},
            {"file_key": "file3", "dto_class": PayrollDTO}
        ]

        all_errors = []
        all_parsed_data = {}
        all_inserted_records = {}

        # PHASE 1: Validate CSVs
        for config in csv_configs:
            file_key = config["file_key"]
            dto_class = config["dto_class"]
            file_content_b64 = data.get(file_key, "")

            if not file_content_b64:
                all_errors.append({
                    "line": 0,
                    "error_message": f"{file_key} est requis",
                    "data": {},
                    "file": file_key
                })
                continue

            try:
                file_content = base64.b64decode(file_content_b64).decode('utf-8')
                print(f"Decoded {file_key} content: {file_content[:100]}...", "CSV Debug")
            except Exception as e:
                all_errors.append({
                    "line": 0,
                    "error_message": f"Erreur de décodage Base64 pour {file_key}: {str(e)}",
                    "data": {},
                    "file": file_key
                })
                continue

            error_list, parsed_data = Service.import_csv(file_content.encode('utf-8'), dto_class)
            print(f"{file_key} parsing completed. Records: {len(parsed_data)}, Errors: {len(error_list)}", "CSV Parsing")

            if error_list:
                for error in error_list:
                    error["file"] = file_key
                all_errors.extend(error_list)

            if not parsed_data and not error_list:
                all_errors.append({
                    "line": 0,
                    "error_message": f"Aucune donnée valide trouvée dans {file_key}",
                    "data": {},
                    "file": file_key
                })
                continue

            all_parsed_data[dto_class.__name__] = parsed_data

        # Split parsed data into separate lists
        employee_dtos = all_parsed_data.get(EmployeeDTO.__name__, [])
        salary_structure_dtos = all_parsed_data.get(SalaryDTO.__name__, [])
        payroll_dtos = all_parsed_data.get(PayrollDTO.__name__, [])

        # Skip payroll if employees fail 
        if not employee_dtos and any(e["file"] == "file3" for e in all_errors):
            frappe.local.response["status"] = "error"
            frappe.local.response["message"] = "Échec de la validation des employés. Le traitement du payroll a été ignoré."
            frappe.local.response["validation_errors"] = all_errors
            frappe.local.response["inserted_records"] = all_inserted_records
            return

        # PHASE 2: Pre-transaction setup
        setup_errors = setup_hrms_data(employee_dtos, salary_structure_dtos)
        if setup_errors:
            all_errors.extend(setup_errors)
            frappe.local.response["status"] = "error"
            frappe.local.response["message"] = "Échec de la configuration initiale."
            frappe.local.response["validation_errors"] = all_errors
            frappe.local.response["inserted_records"] = all_inserted_records
            return

        # PHASE 3: Process CSVs in transaction
        try:
            # Essayer de démarrer une transaction
            try:
                frappe.db.begin()
                print("Transaction started", "CSV Transaction")
            except Exception as tx_error:
                print(f"Could not start transaction: {str(tx_error)}", "CSV Transaction")
                # Continuer sans transaction explicite

            # Process Employees
            if employee_dtos:
                result = insert_employees(employee_dtos)
                all_inserted_records["file1"] = result["created"]
                all_errors.extend([dict(err, file="file1") for err in result["errors"]])
                print(f"Employee insertion: Created={len(result['created'])}, Errors={len(result['errors'])}", "Employee Insertion")

            # Process Salary Structures
            if salary_structure_dtos:
                result = insert_salary_components(salary_structure_dtos)
                all_inserted_records["file2"] = result["created"]
                all_errors.extend([dict(err, file="file2") for err in result["errors"]])

                result = insert_salary_structures(salary_structure_dtos, payroll_dtos)
                all_inserted_records["file2"].extend(result["created"])
                all_errors.extend([dict(err, file="file2") for err in result["errors"]])

            # Process Payroll
            if payroll_dtos:
                result = insert_salary_assignments(payroll_dtos)
                all_inserted_records["file3"] = result["created"]
                all_errors.extend([dict(err, file="file3") for err in result["errors"]])

                result = insert_salary_slips(payroll_dtos)
                all_inserted_records["file3"].extend(result["created"])
                all_errors.extend([dict(err, file="file3") for err in result["errors"]])

            # PHASE 4: Commit or rollback
            if all_errors:
                try:
                    frappe.db.rollback()
                    print("Transaction rolled back due to errors", "CSV Transaction")
                except Exception as rb_error:
                    print(f"Could not rollback transaction: {str(rb_error)}", "CSV Transaction")
                frappe.local.response["status"] = "error"
                frappe.local.response["message"] = "Certaines insertions ont échoué. Toutes les modifications ont été annulées."
                frappe.local.response["validation_errors"] = all_errors
                frappe.local.response["inserted_records"] = all_inserted_records
            else:
                try:
                    frappe.db.commit()
                    print("Transaction committed successfully", "CSV Transaction")
                except Exception as commit_error:
                    print(f"Could not commit transaction: {str(commit_error)}", "CSV Transaction")
                frappe.local.response["status"] = "success"
                frappe.local.response["message"] = "Tous les CSV ont été importés avec succès."
                frappe.local.response["validation_errors"] = []
                frappe.local.response["inserted_records"] = all_inserted_records

        except Exception as e:
            try:
                frappe.db.rollback()
                print(f"Transaction rolled back due to exception: {str(e)}", "CSV Transaction")
            except Exception as rb_error:
                print(f"Could not rollback after exception: {str(rb_error)}", "CSV Transaction")
            
            frappe.local.response["status"] = "error"
            frappe.local.response["message"] = f"Erreur lors de l'insertion: {str(e)}"
            frappe.local.response["validation_errors"] = all_errors + [{
                "line": 0,
                "error_message": f"Erreur lors de l'insertion: {str(e)}",
                "data": {},
                "file": "global"
            }]
            frappe.local.response["inserted_records"] = all_inserted_records
            print(f"Insertion error: {str(e)}", "CSV Insertion")

    except Exception as e:
        frappe.local.response["status"] = "error"
        frappe.local.response["message"] = f"Erreur inattendue: {str(e)}"
        frappe.local.response["validation_errors"] = all_errors + [{
            "line": 0,
            "error_message": f"Erreur inattendue: {str(e)}",
            "data": {},
            "file": "global"
        }]
        frappe.local.response["inserted_records"] = all_inserted_records
        print(f"Unexpected error: {str(e)}", "CSV Error")

    return
