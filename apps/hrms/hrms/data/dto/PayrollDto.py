import frappe
from frappe import _
from frappe.utils import getdate, flt
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from frappe.types import DF

@dataclass
class PayrollDTO:
    mois: str
    ref_employe: str
    salaire_base: float
    salaire: str

    @staticmethod
    def from_dict(data: dict) -> 'PayrollDTO':
        """Create PayrollDTO from CSV row, trimming headers."""
        trimmed_data = {key.strip().replace(" ", "_").lower(): value for key, value in data.items()}
        return PayrollDTO(
            mois=trimmed_data.get("mois", ""),
            ref_employe=trimmed_data.get("ref_employe", "").strip(),
            salaire_base=flt(trimmed_data.get("salaire_base", 0)),
            salaire=trimmed_data.get("salaire", "").strip()
        )

    @staticmethod
    def validate_mois(data):
        if not data:
            frappe.throw(_("Le champ 'mois' est obligatoire"))
        try:
            getdate(data)
        except ValueError:
            frappe.throw(_("Le champ 'mois' doit être une date valide"))

    @staticmethod
    def validate_ref_employe(data):
        if not data:
            frappe.throw(_("Le champ 'ref_employe' est obligatoire"))

    @staticmethod
    def validate_salaire_base(data):
        if not data:
            frappe.throw(_("Le champ 'salaire_base' est obligatoire"))
        try:
            qty = float(data)
            if qty <= 0:
                frappe.throw(_("Le salaire de base doit être supérieur à 0"))
        except ValueError:
            frappe.throw(_("Le salaire de base doit être un nombre valide"))

    @staticmethod
    def validate_salaire(data):
        if not data:
            frappe.throw(_("Le champ 'salaire' est obligatoire"))

    def validateAll(self, fieldName, data):
        """Validate the data for the given fieldName by calling the appropriate validation method."""
        validators = {
            "mois": self.__class__.validate_mois,
            "ref_employe": self.__class__.validate_ref_employe,
            "salaire_base": self.__class__.validate_salaire_base,
            "salaire": self.__class__.validate_salaire
        }
        validator = validators.get(fieldName)
        if validator:
            validator(data)
        else:
            frappe.throw(_(f"Aucune méthode de validation n'existe pour le champ '{fieldName}'"))