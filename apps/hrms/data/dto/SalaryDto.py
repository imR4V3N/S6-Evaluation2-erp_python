import frappe
from frappe import _
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from frappe.types import DF

@dataclass
class SalaryDTO:
    salary_structure: str
    name: str
    abbr: str
    type: str
    valeur: str
    company: str

    @staticmethod
    def from_dict(data: dict) -> 'SalaryDTO':
        """Create SalaryDTO from CSV row, trimming headers."""
        trimmed_data = {key.strip().replace(" ", "_").lower(): value for key, value in data.items()}
        return SalaryDTO(
            salary_structure=trimmed_data.get("salary_structure", "").strip(),
            name=trimmed_data.get("name", "").strip(),
            abbr=trimmed_data.get("abbr", "").strip(),
            type=trimmed_data.get("type", "").strip(),
            valeur=trimmed_data.get("valeur", "").strip(),
            company=trimmed_data.get("company", "").strip()
        )

    @staticmethod
    def validate_salary_structure(data):
        if not data:
            frappe.throw(_("Le champ 'salary_structure' est obligatoire"))

    @staticmethod
    def validate_name(data):
        if not data:
            frappe.throw(_("Le champ 'name' est obligatoire"))

    @staticmethod
    def validate_abbr(data):
        if not data:
            frappe.throw(_("Le champ 'abbr' est obligatoire"))

    @staticmethod
    def validate_type(data):
        if not data:
            frappe.throw(_("Le champ 'type' est obligatoire"))

    @staticmethod
    def validate_valeur(data):
        if not data:
            frappe.throw(_("Le champ 'valeur' est obligatoire"))

    @staticmethod
    def validate_company(data):
        pass  # Optional field, no validation required

    def validateAll(self, fieldName, data):
        """Validate the data for the given fieldName by calling the appropriate validation method."""
        validators = {
            "salary_structure": self.__class__.validate_salary_structure,
            "name": self.__class__.validate_name,
            "abbr": self.__class__.validate_abbr,
            "type": self.__class__.validate_type,
            "valeur": self.__class__.validate_valeur,
            "company": self.__class__.validate_company
        }
        validator = validators.get(fieldName)
        if validator:
            validator(data)
        else:
            frappe.throw(_(f"Aucune méthode de validation n'existe pour le champ '{fieldName}'"))