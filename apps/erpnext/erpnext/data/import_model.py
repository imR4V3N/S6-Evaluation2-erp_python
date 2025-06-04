import datetime
import random
import frappe
import csv
import io

def create_suppliers(suppliers):
    try:
        # Get valid values from ERPNext
        valid_countries = {c["name"] for c in frappe.get_all("Country", fields=["name"])}
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

                # Check if supplier already exists
                if frappe.db.exists("Supplier", {"supplier_name": supplier_name}):
                    frappe.msgprint(f"Supplier {supplier_name} already exists", title="Duplicate Supplier", indicator="yellow")
                    continue

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
    try:
        # Fetch valid reference values
        valid_warehouses = {w["name"] for w in frappe.get_all("Warehouse", fields=["name"])}
        valid_purposes = {"Purchase", "Material Issue", "Material Transfer", "Manufacture", "Material Receipt"}
        valid_item_groups = set(frappe.db.get_all("Item Group", pluck="name"))

        quotations = {}
        errors = []
        
        # First pass: Create all material requests
        for idx, quotation in enumerate(quotations_dict, start=1):
            ref = quotation.get("ref")
            if ref not in quotations:
                try:
                    date = quotation.get("date")
                    required_by = quotation.get("required_by")
                    target_warehouse = "All Warehouses - ITU"
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

                    # Create the Material Request
                    quotations[ref] = frappe.get_doc({
                        "doctype": "Material Request",
                        "transaction_date": date,
                        "required_by": required_by,
                        "schedule_date": required_by,  # Added this to ensure it's set
                        "set_warehouse": target_warehouse,
                        "purpose": purpose,
                        "items": []
                    })
                    
                except Exception as e:
                    errors.append(f"<b>Line {idx}</b> - {str(e)}")

        # Second pass: Create or check items and add them to the material requests
        for idx, quotation in enumerate(quotations_dict, start=1):
            ref = quotation.get("ref")
            if ref in quotations:
                try:
                    item_name = quotation.get("item_name")
                    item_group = quotation.get("item_groupe")
                    required_by = quotation.get("required_by")
                    quantity = quotation.get("quantity")
                    target_warehouse = "All Warehouses - ITU"

                    # Validation
                    if not item_name:
                        raise Exception("Missing 'item_name'")

                    if not item_group:
                        raise Exception(f"Invalid or missing 'item_group': {item_group}")
                    
                    # Check if item exists first
                    item_exists = frappe.db.exists("Item", {"item_name": item_name})
                    
                    # If item doesn't exist, create it
                    if not item_exists:
                        # Check if item group exists, create it if not
                        if item_group not in valid_item_groups:
                            try:
                                if not frappe.db.exists("Item Group", {"item_group_name": item_group}):
                                    frappe.get_doc({
                                        "doctype": "Item Group",
                                        "item_group_name": item_group,
                                        "parent_item_group": "All Item Groups",
                                        "is_group": 0
                                    }).insert(ignore_permissions=True)
                                    valid_item_groups.add(item_group)
                            except Exception as e:
                                raise Exception(f"Failed to create missing item_group '{item_group}': {str(e)}")
                        
                        # Create the item
                        try:
                            frappe.get_doc({
                                "doctype": "Item",
                                "item_code": item_name,
                                "item_name": item_name,
                                "item_group": item_group,
                                "stock_uom": "Nos",
                                "is_stock_item": 1
                            }).insert(ignore_permissions=True)
                            frappe.msgprint(f"Item {item_name} created successfully", title="Item Creation")
                        except frappe.DuplicateEntryError:
                            frappe.msgprint(f"Item {item_name} already exists", title="Duplicate Name", indicator="red")
                    
                    # Now add the item to the material request
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

                    # Add the item to the material request
                    quotations[ref].append("items", {
                        "item_code": item_name,
                        "item_name": item_name,
                        "item_group": item_group,
                        "schedule_date": required_by,
                        "qty": quantity,
                        "warehouse": target_warehouse
                    })
                    
                except Exception as e:
                    errors.append(f"<b>Line {idx}</b> (Material Request: {ref}) - {str(e)}")

        # Insert all material requests
        inserted_material_requests = {}
        for ref, material_request in quotations.items():
            try:
                if len(material_request.items) > 0:
                    material_request.insert(ignore_permissions=True)
                    material_request.submit()
                    inserted_material_requests[ref] = material_request
                else:
                    errors.append(f"Material Request {ref} has no items and was not created")
            except Exception as e:
                errors.append(f"Failed to insert Material Request {ref}: {str(e)}")

        if errors:
            frappe.throw(
                "<h4>Failed to create some material requests:</h4><ul><li>" +
                "</li><li>".join(errors) +
                "</li></ul>",
                title="Material Request Import Failed"
            )

        return inserted_material_requests

    except Exception as e:
        frappe.throw(f"Fatal error during quotation import: {str(e)}", title="Critical Error")

def create_request_for_quotation(material_requests, quotation_suppliers):
    try:
        # Fetch valid reference values
        valid_suppliers = {w["name"] for w in frappe.get_all("Supplier", fields=["name"])}
        quotations = {}
        errors = []

        # First create all Request for Quotations based on Material Requests
        for ref, material_request in material_requests.items():
            try:
                material_request.reload()
                rfq = frappe.get_doc({
                    "doctype": "Request for Quotation",
                    "transaction_date": frappe.utils.nowdate(),
                    "status": "Draft",
                    "message_for_supplier": "Please quote your best prices and delivery times.",
                    "items": [],
                    "suppliers": []
                })
                
                # Add material request items to RFQ
                for item in material_request.items:
                    rfq.append("items", {
                        "item_code": item.item_code,
                        "item_name": item.item_name,
                        "description": item.description or item.item_name,
                        "qty": item.qty,
                        "uom": item.uom or "Nos",
                        "conversion_factor": 1.0,
                        "warehouse": item.warehouse,
                        "material_request": material_request.name,
                        "material_request_item": item.name
                    })
                
                # Store the RFQ for further processing
                quotations[ref] = rfq
                
            except Exception as e:
                errors.append(f"Error creating RFQ from Material Request {material_request.name}: {str(e)}")

        # Now add suppliers to the RFQs
        for idx, quotation_supplier in enumerate(quotation_suppliers, start=1):
            ref = quotation_supplier.get("ref_request_quotation")
            if ref in quotations:
                try:
                    supplier = quotation_supplier.get("supplier")
                    
                    # Validate supplier
                    if not supplier:
                        raise Exception(f"Missing 'supplier' for RFQ reference {ref}")
                    
                    if supplier not in valid_suppliers:
                        raise Exception(f"Invalid supplier '{supplier}' - not found in database")

                    # Add supplier to RFQ
                    quotations[ref].append("suppliers", {
                        "supplier": supplier,
                        "supplier_name": supplier,
                        "email_id": "",  # Add email if available
                        "contact": "",   # Add contact if available
                        "send_email": 0  # Set to 1 if you want to send email
                    })

                except Exception as e:
                    errors.append(f"<b>Line {idx}</b> (RFQ supplier: {quotation_supplier.get('supplier', 'UNKNOWN')}) - {str(e)}")

        # Insert and submit all RFQs
        inserted_rfqs = {}
        for ref, rfq in quotations.items():
            try:
                if len(rfq.suppliers) > 0 and len(rfq.items) > 0:
                    rfq.insert(ignore_permissions=True)
                    rfq.submit()
                    inserted_rfqs[ref] = rfq
                    
                    # Create Supplier Quotations from RFQ
                    for supplier_entry in rfq.suppliers:
                        try:
                            sq = frappe.get_doc({
                                "doctype": "Supplier Quotation",
                                "supplier": supplier_entry.supplier,
                                "currency": frappe.defaults.get_global_default("currency"),
                                "buying_price_list": frappe.db.get_single_value("Buying Settings", "buying_price_list") or "Standard Buying",
                                "transaction_date": frappe.utils.nowdate(),
                                "valid_till": frappe.utils.add_days(frappe.utils.nowdate(), 30),
                                "supplier_quotation_details": "",
                                "terms": "",
                                "items": []
                            })
                            
                            # Link RFQ to Supplier Quotation
                            sq.rfq = rfq.name
                            
                            # Add items from RFQ to Supplier Quotation
                            for item in rfq.items:
                                sq.append("items", {
                                    "item_code": item.item_code,
                                    "item_name": item.item_name,
                                    "description": item.description,
                                    "qty": item.qty,
                                    "rate": 0.0,  # Default price
                                    "uom": item.uom,
                                    "stock_uom": item.stock_uom or "Nos",
                                    "warehouse": item.warehouse,
                                    "request_for_quotation": rfq.name,
                                    "request_for_quotation_item": item.name,
                                    "material_request": item.material_request,
                                    "material_request_item": item.material_request_item
                                })
                            
                            # Insert Supplier Quotation as draft
                            sq.insert(ignore_permissions=True)
                            
                        except Exception as e:
                            errors.append(f"Failed to create Supplier Quotation for RFQ {rfq.name}, Supplier {supplier_entry.supplier}: {str(e)}")
            except Exception as e:
                errors.append(f"Failed to insert RFQ for reference {ref}: {str(e)}")

        if errors:
            frappe.throw(
                "<h4>Failed to create some Request for Quotations:</h4><ul><li>" +
                "</li><li>".join(errors) +
                "</li></ul>",
                title="RFQ Import Failed"
            )

        return inserted_rfqs

    except Exception as e:
        frappe.throw(f"Fatal error during RFQ creation: {str(e)}", title="Critical Error")

def fill_blank_items(items):
    updated_items = []

    for item in items:
        updated = item.copy()
        updated.setdefault('stock_uom', "Nos")
        updated_items.append(updated)

    return updated_items

def fill_blank_suppliers(suppliers):
    supplier_groups = [sg["name"] for sg in frappe.get_all("Supplier Group", fields=["name"])]
    
    updated_suppliers = []

    for supplier in suppliers:
        updated = supplier.copy()
        # Fill missing but required ERPNext fields
        updated.setdefault('supplier_group', random.choice(supplier_groups) if supplier_groups else "All Supplier Groups")
        updated.setdefault('tax_id', "AB1234567")  # Default tax ID
        updated.setdefault('default_currency', 'USD')  # Default currency

        updated_suppliers.append(updated)

    return updated_suppliers


def create_doctypes(quotations, suppliers, quotation_suppliers):
    try:
        # Fill blank columns with default data
        suppliers = fill_blank_suppliers(suppliers)
        quotations = fill_blank_items(quotations)
        
        # Insert suppliers first
        create_suppliers(suppliers)
        
        # Create material requests from quotations
        material_requests = create_material_requests(quotations)
        
        # Create RFQs and link suppliers
        if material_requests:
            create_request_for_quotation(material_requests, quotation_suppliers)

        # Return success message
        return "Data imported successfully"
    
    except Exception as e:
        frappe.throw(f"Error in data import process: {str(e)}", title="Import Failed")


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