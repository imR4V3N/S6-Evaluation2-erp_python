# apps/hrms/hrms/data/insert_controller.py

import frappe
import json
from frappe import _
from frappe.client import insert_many

@frappe.whitelist(allow_guest=False)
def create_salary_documents(assignment_json, slip_json):
    try:
        # Si les JSON sont envoyés sous forme de chaînes, les parser
        if isinstance(assignment_json, str):
            assignment_json = json.loads(assignment_json)
        if isinstance(slip_json, str):
            slip_json = json.loads(slip_json)

        if not assignment_json.get("docs") or not slip_json.get("docs"):
            frappe.throw(_("Salaire deja existante pour les mois demandees."))

        insert_many(assignment_json["docs"])
        insert_many(slip_json["docs"])

        return {"message": "Les documents ont ete generer avec succes."}

    except Exception as e:
        frappe.db.rollback()
        frappe.throw(_("Erreur lors de l'insertion des documents : {0}").format(str(e)))
