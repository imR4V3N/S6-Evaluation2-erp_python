import csv
import frappe
from frappe.utils import getdate, get_datetime, get_time
from datetime import datetime
from io import StringIO
from hrms.data.dto.EmployeeDto import EmployeeDTO
from hrms.data.dto.SalaryDto import SalaryDTO
from hrms.data.dto.PayrollDto import PayrollDTO

class Service:
    @staticmethod
    def import_csv(file_content, dto_class):
        result_list = []
        error_list = []
        line_number = 1  # Start from 1 for header row

        print(f"Starting CSV parsing for DTO: {dto_class.__name__}")

        try:
            print(f"Decoding file content (size: {len(file_content)} bytes)")
            reader = StringIO(file_content.decode('utf-8') if isinstance(file_content, bytes) else file_content)
            csv_reader = csv.DictReader(reader)
            # Trim and normalize headers
            csv_reader.fieldnames = [field.strip().replace(" ", "_").lower() for field in csv_reader.fieldnames]

            print(f"CSV headers after trimming: {csv_reader.fieldnames}")

            for row in csv_reader:
                line_number += 1
                print(f"Processing row {line_number}: {row}")
                row_errors = []
                record = None

                # Create DTO instance
                try:
                    dto = dto_class.from_dict(row)
                    # Validate each field using validateAll
                    for fieldname, value in vars(dto).items():
                        if value:  # Only validate non-empty values
                            try:
                                dto.validateAll(fieldname, value)
                            except Exception as e:
                                row_errors.append(f"Field '{fieldname}' validation failed: {str(e)}")
                                error_list.append({
                                    "line": line_number,
                                    "error_message": str(e),
                                    "data": row
                                })
                    # If no validation errors, add DTO to result list
                    if not row_errors:
                        record = dto
                except Exception as e:
                    error_list.append({
                        "line": line_number,
                        "error_message": f"Failed to create DTO: {str(e)}",
                        "data": row
                    })

                # Add to result list if no errors
                if record and not row_errors:
                    result_list.append(record)
                    print(f"Added DTO to result list: {record}")

            print(f"CSV parsing completed. Total records parsed: {len(result_list)}, Errors: {len(error_list)}")
            return error_list, result_list

        except Exception as e:
            print(f"Error parsing CSV: {str(e)}")
            error_list.append({
                "line": 1,
                "error_message": f"Failed to parse CSV: {str(e)}",
                "data": {}
            })
            return error_list, result_list

    @staticmethod
    def parse_value(field_type, value):
        print(f"Parsing value '{value}' for field type: {field_type}")
        try:
            if field_type in ['Int', 'Integer']:
                return int(value)
            elif field_type in ['Float', 'Currency', 'Percent']:
                return float(value)
            elif field_type == 'Check':
                return 1 if value.lower() in ['true', '1', 'yes'] else 0
            elif field_type in ['Data', 'Long Text']:
                return value
            elif field_type == 'Text':
                return value
            elif field_type == 'Date':
                parsed_date = getdate(value)
                print(f"Parsed date: {parsed_date}")
                return parsed_date
            elif field_type == 'Datetime':
                return get_datetime(value)
            elif field_type == 'Time':
                return get_time(value)
            elif field_type == 'Link':
                return value
            elif field_type == 'Select':
                return value
            elif field_type in ['Table', 'Table MultiSelect']:
                parsed_list = [v.strip() for v in value.split(',')]
                print(f"Parsed list: {parsed_list}")
                return parsed_list
            else:
                print(f"Unsupported field type: {field_type}")
                return value
        except Exception as e:
            print(f"Error parsing value '{value}' for type '{field_type}': {str(e)}")
            return None