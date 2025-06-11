import pandas as pd

def convert_excel_date(x):
    """Convert Excel date format to YYYY-MM-DD string."""
    if pd.isna(x):
        print(f"Converting {x}")
        return '1998-04-02'
    try:
        # Try parsing as Excel date (days since 1900-01-01)
        if isinstance(x, (int, float)):
            return (pd.Timestamp('1900-01-01') + pd.Timedelta(days=int(x))).strftime('%Y-%m-%d')
        # Try parsing as regular date string
        return pd.to_datetime(x).strftime('%Y-%m-%d')
    except:
        return None

def clean_data(data: pd.DataFrame) -> pd.DataFrame:
    """Clean the data."""
    # Convert specific columns to appropriate types
    data = data.astype({
        'insurance_type': str,
        'postal_code': str,
        'address': str,
        'city': str,
        'province': str,
        'country': str,
        'name': str,
        'move_in_year': str,
        'occupants': str,
        'num_claims': str,
        'num_cancellations': str,
        'num_fire_extinguishers': str,
        'num_mortgages': str,
        'email': str,
    })
    
    # Format phone numbers to remove scientific notation and decimal points
    data['phone'] = data['phone'].astype(str).apply(
        lambda x: x.split('.')[0] if '.' in x else x
    )
    
    # Convert boolean columns
    bool_columns = [
        'active_home_insurance',
        'ever_insured',
        'multiline_discount',
        'has_monitored_fire_alarm',
        'has_deadbolt_locks',
        'has_monitored_burglar_alarm',
        'has_sprinkler_system',
        'occupants_non_smokers'
    ]
    for col in bool_columns:
        data[col] = data[col].fillna(False).astype(bool)
    
    # Handle unit/apt field - convert nan to None
    data['unit_apt'] = data['unit_apt'].where(pd.notna(data['unit_apt']), None)
    
    # Convert date_of_birth from Excel date format to YYYY-MM-DD string
    data['date_of_birth'] = data['date_of_birth'].apply(convert_excel_date)
    
    # Convert move_in_year to string and handle None
    data['move_in_year'] = data['move_in_year'].where(pd.notna(data['move_in_year']), None)
    
    # Convert all remaining nan values to None
    data = data.where(pd.notna(data), None)

    return data

__all__ = ['clean_data', 'convert_excel_date']