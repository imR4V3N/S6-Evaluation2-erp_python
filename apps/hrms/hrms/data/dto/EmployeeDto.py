import frappe
from frappe import _
from frappe.utils import getdate
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from frappe.types import DF

@dataclass
class EmployeeDTO:
    ref: str
    nom: str
    prenom: str
    genre: str
    date_embauche: str
    date_naissance: Optional[str]
    company: str

    @staticmethod
    def from_dict(data: dict) -> 'EmployeeDTO':
        """Create EmployeeDTO from CSV row, trimming headers."""
        trimmed_data = {key.strip().replace(" ", "_").lower(): value for key, value in data.items()}
        return EmployeeDTO(
            ref=trimmed_data.get("ref", "").strip(),
            nom=trimmed_data.get("nom", "").strip(),
            prenom=trimmed_data.get("prenom", "").strip(),
            genre=trimmed_data.get("genre", "").strip(),
            date_embauche=trimmed_data.get("date_embauche", ""),
            date_naissance=trimmed_data.get("date_naissance", ""),
            company=trimmed_data.get("company", "").strip() or "My Company"
        )

    @staticmethod
    def validate_ref(data):
        if not data:
            frappe.throw(_("Le champ 'ref' est obligatoire"))
        if frappe.db.exists("Employee", {"employee": data}):
            frappe.throw(_("Un employé avec le ref '{0}' existe déjà").format(data))

    @staticmethod
    def validate_nom(data):
        if not data:
            frappe.throw(_("Le champ 'nom' est obligatoire"))

    @staticmethod
    def validate_prenom(data):
        if not data:
            frappe.throw(_("Le champ 'prenom' est obligatoire"))

    @staticmethod
    def validate_genre(data):
        if not data:
            frappe.throw(_("Le champ 'genre' est obligatoire"))
        if data.lower() not in ['masculin', 'feminin', 'male', 'female', 'm', 'f']:
            frappe.throw(_("Le champ 'genre' doit être 'Masculin' ou 'Feminin'"))

    @staticmethod
    def validate_date_embauche(data):
        if not data:
            frappe.throw(_("Le champ 'date_embauche' est obligatoire"))
        try:
            getdate(data)
        except ValueError:
            frappe.throw(_("Le champ 'date_embauche' doit être une date valide"))

    @staticmethod
    def validate_datenaissance(data):
        if data:
            try:
                getdate(data)
            except ValueError:
                frappe.throw(_("Le champ 'date_naissance' doit être une date valide"))

    @staticmethod
    def validate_company(data):
        if not data:
            frappe.throw(_("Le champ 'company' est obligatoire"))

    
    def validateAll(self, fieldName, data):
        """Validate the data for the given fieldName by calling the appropriate validation method."""
        validators = {
            "ref": self.__class__.validate_ref,
            "nom": self.__class__.validate_nom,
            "prenom": self.__class__.validate_prenom,
            "genre": self.__class__.validate_genre,
            "date_embauche": self.__class__.validate_date_embauche,
            "date_naissance": self.__class__.validate_datenaissance,
            "company": self.__class__.validate_company
        }
        validator = validators.get(fieldName)
        if validator:
            validator(data)
        else:
            frappe.throw(_(f"Aucune méthode de validation n'existe pour le champ '{fieldName}'"))