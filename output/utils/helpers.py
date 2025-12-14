def format_monetary(amount):
    """Format a monetary amount with currency symbol"""
    if amount is None:
        return "$0.00"
    return f"${amount:,.2f}"
