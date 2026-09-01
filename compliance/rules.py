# =========================================================
# LEGAL METROLOGY COMPLIANCE RULES
# =========================================================

MANDATORY_DECLARATIONS = [

    {
        'code': 'MANUFACTURER_DETAILS',
        'name': 'Manufacturer / Packer / Importer Details',
        'description':
            'Name and address of manufacturer, packer or importer.'
    },

    {
        'code': 'NET_QUANTITY',
        'name': 'Net Quantity',
        'description':
            'Net quantity of the packaged commodity.'
    },

    {
        'code': 'MRP',
        'name': 'Maximum Retail Price',
        'description':
            'Maximum Retail Price declaration.'
    },

    {
        'code': 'PACKING_DATE',
        'name': 'Month and Year',
        'description':
            'Month and year of manufacture, packing or import as applicable.'
    },

    {
        'code': 'CONSUMER_CARE',
        'name': 'Consumer Care Details',
        'description':
            'Consumer care contact information.'
    },
]


def get_all_rules():
    """
    Return all compliance rules.
    """

    return MANDATORY_DECLARATIONS