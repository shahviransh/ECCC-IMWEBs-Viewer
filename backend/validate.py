from cerberus import Validator
import re


def validate_request_args(schema, request_args):
    """
    Validates the request arguments using Cerberus and applies additional security checks.
    """
    validator = Validator(schema)
    data = {key: request_args.get(key) for key in schema.keys()}

    if not validator.validate(data):
        return {
            "error": f"Invalid parameters: {getUserValidationError(validator.errors)}"
        }

    # Additional security checks for path traversal and SQL injection
    for key, value in data.items():
        if isinstance(value, str):
            # Check for path traversal
            if re.search(r"(\.\.\/|\.\.\\)", value):
                return {
                    "error": f"Potential path traversal detected in parameter: {key}"
                }

            # Check for SQL injection patterns
            if re.search(
                r"(\bSELECT\b|\bINSERT\b|\bDELETE\b|\bUPDATE\b|\bDROP\b|;|--|\bEXEC\b|\bUNION\b)",
                value,
                re.IGNORECASE,
            ):
                return {
                    "error": f"Potential SQL injection detected in parameter: {key}"
                }

    return validator.document


# Example usage for the /api/get_data endpoint
def validate_get_data_args(request_args):
    schema = {
        "db_tables": {"type": "string", "required": True},
        "columns": {"type": "string", "required": True},
        "id": {
            "type": "string",
            "required": True,
            "regex": r'\["\d+"(,\s*"\d+")*\]|\[\]',
        },
        "start_date": {
            "type": "string",
            "required": True,
            "regex": r"^\d{4}-\d{2}-\d{2}$",
        },
        "end_date": {
            "type": "string",
            "required": True,
            "regex": r"^\d{4}-\d{2}-\d{2}$",
        },
        "date_type": {
            "type": "string",
            "required": True,
            "allowed": ["Time", "Date", "Month", "Year", ""],
        },
        "interval": {
            "type": "string",
            "required": True,
            "default": "daily",
            "regex": r"^[a-zA-Z]+$",
        },
        "method": {"type": "string", "required": True, "default": "[Equal]"},
        "statistics": {"type": "string", "required": True, "default": "[None]"},
    }
    return validate_request_args(schema, request_args)


# Example usage for the /api/export_data endpoint
def validate_export_data_args(request_args):
    schema = {
        "db_tables": {"type": "string", "required": True},
        "columns": {"type": "string", "required": True},
        "id": {
            "type": "string",
            "required": True,
            "regex": r'\["\d+"(,\s*"\d+")*\]|\[\]',
        },
        "start_date": {
            "type": "string",
            "required": True,
            "regex": r"^\d{4}-\d{2}-\d{2}$",
        },
        "end_date": {
            "type": "string",
            "required": True,
            "regex": r"^\d{4}-\d{2}-\d{2}$",
        },
        "date_type": {
            "type": "string",
            "required": True,
            "allowed": ["Time", "Date", "Month", "Year", ""],
        },
        "interval": {
            "type": "string",
            "required": True,
            "default": "daily",
            "regex": r"^[a-zA-Z]+$",
        },
        "method": {"type": "string", "required": True, "default": "[Equal]"},
        "statistics": {"type": "string", "required": True, "default": "[None]"},
        "export_filename": {
            "type": "string",
            "required": True,
            "regex": r"^[a-zA-Z]+$",
        },
        "export_format": {
            "type": "string",
            "required": True,
            "allowed": ["csv", "txt", "xsls", "png", "jpg", "jpeg", "svg", "pdf"],
        },
        "export_path": {"type": "string", "required": True},
        "options": {"type": "string", "required": True},
    }
    return validate_request_args(schema, request_args)


# Example usage for the /api/get_tables endpoint
def validate_get_tables_args(request_args):
    schema = {"db_path": {"type": "string", "required": True}}
    return validate_request_args(schema, request_args)


# Example usage for /api/list_files endpoint
def validate_list_files_args(request_args):
    schema = {"folder_path": {"type": "string", "required": True}}
    return validate_request_args(schema, request_args)


# Example usage for /api/get_table_details endpoint
def validate_get_table_details_args(request_args):
    schema = {"db_tables": {"type": "string", "required": True}}
    return validate_request_args(schema, request_args)


# Example usage for /api/mapbox_shapefile endpoint
def validate_mapbox_shapefile_args(request_args):
    schema = {"file_path": {"type": "string", "required": True}}
    return validate_request_args(schema, request_args)


def getUserValidationError(errors):
    """
    Get user-friendly error messages from Cerberus validation errors.
    """
    # Mapping regex patterns to human-readable messages
    regex_messages = {
        r"^\d{4}-\d{2}-\d{2}$": "should be in the format YYYY-MM-DD (e.g., 2024-01-01).",
        r"^[a-zA-Z]+$": "should only contain alphabetic characters.",
        r'\["\d+"(,\s*"\d+")*\]|\[\]': "should be a numbers quoted and enclosed in square brackets (e.g., ['1','2','3']).",
    }

    error_messages = []
    for field, error in errors.items():
        if isinstance(error, list):
            for e in error:
                if "does not match" in e:
                    # Check if the error is related to regex and map it
                    for pattern, message in regex_messages.items():
                        if pattern in e:
                            error_messages.append(f"{field}: {message}")
                            break
                    else:
                        error_messages.append(f"{field}: {e}")
                else:
                    error_messages.append(f"{field}: {e}")
        else:
            error_messages.append(f"{field}: {error}")

    return ", ".join(error_messages)
