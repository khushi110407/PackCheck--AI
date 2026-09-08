import re


# Mandatory declarations for a basic packaged-commodity check.
# These are the fields our prototype will validate.
MANDATORY_FIELDS = {
    "manufacturer": {
        "label": "Manufacturer / Packer / Importer",
        "severity": "High",
        "rule": "Mandatory declaration",
    },
    "net_quantity": {
        "label": "Net Quantity",
        "severity": "High",
        "rule": "Mandatory declaration",
    },
    "mrp": {
        "label": "MRP",
        "severity": "High",
        "rule": "MRP declaration",
    },
    "manufacturing_date": {
        "label": "Month & Year of Manufacture",
        "severity": "Medium",
        "rule": "Date declaration",
    },
    "consumer_care": {
        "label": "Consumer Care Details",
        "severity": "Medium",
        "rule": "Consumer care declaration",
    },
}


def is_valid_mrp(value):
    """Check whether MRP contains a numeric price."""
    if not value:
        return False

    value = str(value)

    pattern = r"(₹|rs\.?|inr)?\s*\d+(?:\.\d+)?"

    return bool(re.search(pattern, value, re.IGNORECASE))


def is_valid_quantity(value):
    """Check whether net quantity contains a number and valid unit."""
    if not value:
        return False

    value = str(value)

    pattern = (
        r"\d+(?:\.\d+)?\s*"
        r"(kg|g|gm|mg|l|litre|liter|ml)"
    )

    return bool(re.search(pattern, value, re.IGNORECASE))


def check_field(field_name, value):
    """
    Validate one extracted declaration.
    Returns a violation dictionary if invalid, otherwise None.
    """

    field_info = MANDATORY_FIELDS.get(field_name)

    if not field_info:
        return None

    # Missing value
    if value is None or str(value).strip() == "":
        return {
            "rule": field_info["rule"],
            "violation_type": "Missing Declaration",
            "description": (
                f"{field_info['label']} was not detected "
                "in the product label."
            ),
            "declaration": field_info["label"],
            "severity": field_info["severity"],
        }

    # Field-specific validation
    if field_name == "mrp":
        if not is_valid_mrp(value):
            return {
                "rule": field_info["rule"],
                "violation_type": "Invalid MRP Format",
                "description": (
                    "MRP was detected, but the price format "
                    "could not be validated."
                ),
                "declaration": field_info["label"],
                "severity": field_info["severity"],
            }

    if field_name == "net_quantity":
        if not is_valid_quantity(value):
            return {
                "rule": field_info["rule"],
                "violation_type": "Invalid Quantity Format",
                "description": (
                    "Net quantity was detected, but the "
                    "quantity/unit format is invalid."
                ),
                "declaration": field_info["label"],
                "severity": field_info["severity"],
            }

    return None


def calculate_score(total_fields, violations):
    """
    Calculate a simple prototype compliance score.
    """

    if total_fields == 0:
        return 0

    violation_count = len(violations)

    score = 100 - (
        (violation_count / total_fields) * 100
    )

    return round(max(0, score))


def get_status(score):
    """Convert score into compliance status."""

    if score >= 90:
        return "Compliant"

    if score >= 60:
        return "Partially Compliant"

    return "Non-Compliant"


def run_rule_engine(declarations):
    """
    Main Legal Metrology compliance rule engine.

    Input:
        declarations = {
            "manufacturer": "...",
            "net_quantity": "...",
            "mrp": "...",
            "manufacturing_date": "...",
            "consumer_care": "..."
        }

    Output:
        violations
        score
        status
    """

    if not declarations:
        declarations = {}

    violations = []

    for field_name in MANDATORY_FIELDS:
        value = declarations.get(field_name)

        violation = check_field(
            field_name,
            value
        )

        if violation:
            violations.append(violation)

    total_fields = len(MANDATORY_FIELDS)

    score = calculate_score(
        total_fields,
        violations
    )

    status = get_status(score)

    return {
        "total_fields": total_fields,
        "checked_fields": total_fields - len(violations),
        "violations": violations,
        "violation_count": len(violations),
        "score": score,
        "status": status,
    }