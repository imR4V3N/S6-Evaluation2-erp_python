import datetime
import random
import frappe
import csv
import io

def create_suppliers(suppliers):
    try:
        # Get valid values from ERPNext
        valid_countries = {c["name"] for c in frappe.get_all("Country", fields=["name"])}
        # valid_supplier_groups = {sg["name"] for sg in frappe.get_all("Supplier Group", fields=["name"])}
        # valid_currencies = {c["name"] for c in frappe.get_all("Currency", fields=["name"])}
        valid_types = {"Company", "Individual", "Partnership"}  # Adjust as needed

        errors = []

        for idx, supplier in enumerate(suppliers, start=1):
            try:
                supplier_name = supplier.get("supplier_name")
                country = supplier.get("country")
                if(country == "Usa"):
                    country = "United States"

                supplier_type = supplier.get("type")
                supplier_group = supplier.get("supplier_group")
                default_currency = supplier.get("default_currency")
                tax_id = supplier.get("tax_id") or "TEMP123456"

                # Validation checks
                if not supplier_name:
                    raise Exception("Missing 'supplier_name'")
                if not country or country not in valid_countries:
                    raise Exception(f"Invalid or missing 'country': {country}")
                if not supplier_type or supplier_type not in valid_types:
                    raise Exception(f"Invalid or missing 'type': {supplier_type}")
                # if not supplier_group or supplier_group not in valid_supplier_groups:
                #     raise Exception(f"Invalid or missing 'supplier_group': {supplier_group}")
                # if not default_currency or default_currency not in valid_currencies:
                #     raise Exception(f"Invalid or missing 'default_currency': {default_currency}")

                # Create supplier
                doc = frappe.get_doc({
                    "doctype": "Supplier",
                    "supplier_name": supplier_name,
                    "country": country,
                    "type": supplier_type,
                    "supplier_group": supplier_group,
                    "tax_id": tax_id,
                    "default_currency": default_currency
                })
                doc.insert(ignore_permissions=True)
            except Exception as e:
                errors.append(f"<b>Line {idx}</b> (Supplier: <code>{supplier.get('supplier_name', 'UNKNOWN')}</code>) - {str(e)}")

        if errors:
            frappe.throw(
                "<h4>Failed to create some suppliers:</h4><ul><li>" +
                "</li><li>".join(errors) +
                "</li></ul>",
                title="Supplier Import Failed"
            )

    except Exception as e:
        frappe.throw(f"Fatal error during supplier import: {str(e)}", title="Critical Error")

def create_material_requests(quotations_dict):
    # frappe.msgprint(f"create_material_requests", title=None, indicator=None)
    try:
        # Fetch valid reference values
        valid_warehouses = {w["name"] for w in frappe.get_all("Warehouse", fields=["name"])}
        valid_purposes = {"Sales", "Purchase", "Transfer"}  # Adjust based on your use case        
        valid_item_groups = set(frappe.db.get_all("Item Group", pluck="name"))

        quotations = {}
        errors = []

        for idx, quotation in enumerate(quotations_dict, start=1):
            ref = quotation.get("ref")
            if ref not in quotations:
                try:
                    date = quotation.get("date")
                    required_by = quotation.get("required_by")
                    target_warehouse = f"{quotation.get('target_warehouse')}s - ITU"
                    purpose = quotation.get("purpose")


                    # Validate required fields
                    if not date:
                        raise Exception("Missing 'date'")
                    try:
                        date = datetime.datetime.strptime(date, "%d/%m/%Y").strftime("%Y-%m-%d")
                    except ValueError:
                        raise Exception(f"Invalid date format: '{date}' (expected DD/MM/YYYY)")

                    if not required_by:
                        raise Exception("Missing 'required_by'")
                    try:
                        required_by = datetime.datetime.strptime(required_by, "%d/%m/%Y").strftime("%Y-%m-%d")
                    except ValueError:
                        raise Exception(f"Invalid required_by format: '{required_by}' (expected DD/MM/YYYY)")

                    if not target_warehouse or target_warehouse not in valid_warehouses:
                        raise Exception(f"Invalid or missing 'target_warehouse': {target_warehouse}")

                    if not purpose or purpose not in valid_purposes:
                        raise Exception(f"Invalid or missing 'purpose': {purpose}")

                    # Create the Quotation
                    quotations[ref] = frappe.get_doc({
                        "doctype": "Material Request",
                        "transaction_date": date,
                        "required_by": required_by,
                        "target_warehouse": target_warehouse,
                        "purpose": purpose,
                        "items": []
                    })
                    frappe.msgprint(f"{quotations}", title=None, indicator=None)

                except Exception as e:
                    errors.append(f"<b>Line {idx}</b> - {str(e)}")

            try:
                frappe.msgprint(f"Initialization", title=None, indicator=None)

                item_name = quotation.get("item_name")
                item_group = quotation.get("item_groupe")
                required_by = quotation.get("required_by")
                quantity = quotation.get("quantity")
                target_warehouse = f"{quotation.get('target_warehouse')}s - ITU"


                # Validation
                if not item_name:
                    raise Exception("Missing 'item_name'")

                if not item_group:
                    raise Exception(f"Invalid or missing 'item_group': {item_group}")
                
                if item_group not in valid_item_groups:
                    # Try to create the item group
                    try:
                        frappe.get_doc({
                            "doctype": "Item Group",
                            "item_group_name": item_group,
                            "parent_item_group": "All Item Groups",
                            "is_group": 0
                        }).insert(ignore_permissions=True)
                        valid_item_groups.add(item_group)
                    except Exception as e:
                        raise Exception(f"Failed to create missing item_group '{item_group}': {str(e)}")

                if not required_by:
                    raise Exception("Missing 'required_by'")
                try:
                    required_by = datetime.datetime.strptime(required_by, "%d/%m/%Y").strftime("%Y-%m-%d")
                except ValueError:
                    raise Exception(f"Invalid 'required_by' format: {required_by} (expected DD/MM/YYYY)")

                if quantity is None:
                    raise Exception("Missing 'quantity'")
                try:
                    quantity = float(quotation['quantity'])
                    if quantity <= 0:
                        raise Exception(f"Invalid 'quantity': {quantity} (must be a positive number)")
                except (ValueError, TypeError, KeyError):
                    raise Exception(f"Invalid or missing 'quantity': {quotation.get('quantity')} (must be a positive number)")

                if not target_warehouse or target_warehouse not in valid_warehouses:
                    raise Exception(f"Invalid or missing 'target_warehouse': {target_warehouse}")

                # Create Material Request Item (or similar)
                # You can adapt this block if you're creating something else
                frappe.msgprint(f"Creation", title=None, indicator=None)
                frappe.get_doc({
                    "doctype": "Item",
                    "item_code": item_name,
                    "item_name": item_name,
                    "item_group": item_group,
                    "stock_uom": "Nos",  # Mandatory field - change if needed
                    "is_stock_item": 1   # Optional but commonly set
                }).insert(ignore_permissions=True)


                quotations[ref].append("items", {
                    "item_code": item_name,
                    "item_name": item_name,
                    "item_group": item_group,
                    "schedule_date": required_by,
                    "qty": quantity,
                    "warehouse": target_warehouse
                })
                frappe.msgprint(f"{quotations}", title=None, indicator=None)

            except Exception as e:
                errors.append(f"<b>Line {idx}</b> ( Material Request: - {str(e)}")

        frappe.msgprint(f"{quotations}", title=None, indicator=None)
        for _, quotation in quotations.items():
            quotation.insert(ignore_permissions=True)
            quotation.submit()

        if errors:
            frappe.throw(
                "<h4>Failed to create some quotations:</h4><ul><li>" +
                "</li><li>".join(errors) +
                "</li></ul>",
                title="Quotation Import Failed"
            )

        return quotations

    except Exception as e:
        frappe.throw(f"Fatal error during quotation import: {str(e)}", title="Critical Error")

def create_request_for_quotation(material_requests, quotation_suppliers):
    # frappe.msgprint(f"create_request_for_quotation", title=None, indicator=None)
    quotations = {}
    for i, material_request in material_requests.items():
        try:
            material_request.reload()
            rfq = frappe.get_doc({
                "doctype": "Request for Quotation",
                "material_request": material_request.name,
                "message_for_supplier": "Please quote your best prices and delivery times.",  # <-- Add this line
                "request_date": frappe.utils.nowdate(),  # Today's date for RFQ
                "items": [],
                "suppliers": []
            })
            
            for item in material_request.items:
                rfq.append("items", {
                    "item_code": item.item_code,
                    "item_name": item.item_name,
                    "description": item.description,
                    "qty": item.qty,
                    "uom": item.uom,
                    "conversion_factor": 1.0,
                    "warehouse": item.warehouse,
                    "rate": 0.0  # You can leave the rate as 0 or calculate based on other logic
                })
            quotations[i] = rfq
            # frappe.msgprint(f"{quotations}", title=None, indicator=None)
        except Exception as e:
            frappe.throw(f"Error creating RFQ from Material Request: {str(e)}")

    try:
        # Fetch valid reference values
        valid_suppliers = {w["name"] for w in frappe.get_all("Supplier", fields=["name"])}
        errors = []

        for idx, quotation_supplier in enumerate(quotation_suppliers, start=1):
            ref = quotation_supplier.get("ref_request_quotation")
            if ref in quotations:
                try:
                    supplier = quotation_supplier.get("supplier")

                    if not supplier or supplier not in valid_suppliers:
                        raise Exception(f"Invalid or missing 'supplier': {supplier}")

                    quotations[ref].append("suppliers", {
                        "supplier": supplier,
                        "supplier_name": supplier,
                        "quotation_required": 1
                    })

                except Exception as e:
                    errors.append(f"<b>Line {idx}</b> - {str(e)}")
        # frappe.msgprint(f"{quotations}", title=None, indicator=None)

        for _, quotation in quotations.items():
            quotation.insert(ignore_permissions=True)
            quotation.submit()

        if errors:
            frappe.throw(
                "<h4>Failed to create some quotations:</h4><ul><li>" +
                "</li><li>".join(errors) +
                "</li></ul>",
                title="Quotation Import Failed"
            )

    except Exception as e:
        frappe.throw(f"Fatal error during quotation import: {str(e)}", title="Critical Error")

def fill_blank_items(items):
    updated_items = []

    for supplier in items:
        updated = supplier.copy()
        updated.setdefault('stock_uom', "Nos")

        updated_items.append(updated)

    return updated_items

def fill_blank_suppliers(suppliers):
    supplier_groups = [sg["name"] for sg in frappe.get_all("Supplier Group", fields=["name"])]
    currencies = [c["name"] for c in frappe.get_all("Currency", fields=["name"])]

    updated_suppliers = []

    for supplier in suppliers:
        updated = supplier.copy()
        # Fill missing but required ERPNext fields
        updated.setdefault('supplier_group', random.choice(supplier_groups))
        updated.setdefault('tax_id', "AB1234567")  # e.g., AB1234567
        # fake.bothify(text='??#######')
        updated.setdefault('default_currency', random.choice(currencies))

        updated_suppliers.append(updated)

    return updated_suppliers

def create_doctypes(quotations, suppliers, quotation_suppliers):
    # fill blank columns with random data
    suppliers = fill_blank_suppliers(suppliers)
    quotations = fill_blank_items(quotations)
    # insert into select suppliers
    create_suppliers(suppliers)
    # insert into select quotations
    material_requests = create_material_requests(quotations)
    # insert into select quotations_suppliers
    create_request_for_quotation(material_requests, quotation_suppliers)

    # return message
    return "Data imported successfuly"


def read_csv_file_as_dict(file_storage):
    """
    Takes a Werkzeug FileStorage object (from frappe.request.files)
    and returns a list of dicts representing the CSV content.
    """
    try:
        # Read binary content and decode
        content = file_storage.read().decode('utf-8-sig')  # UTF-8 with BOM support
        # Wrap in StringIO so csv can process it like a file
        reader = csv.DictReader(io.StringIO(content))

        return list(reader)
    except Exception as e:
        frappe.throw(f"Failed to read uploaded CSV file: {str(e)}")
        