from bs4 import BeautifulSoup
import re

def extract_insurance_quotes(html_content):
    """
    Extract home insurance quotes from HTML and return as a structured dictionary.
    
    Args:
        html_content (str): HTML content containing insurance quotes
        
    Returns:
        dict: Dictionary with carrier names as keys and premium info as values
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    quotes_dict = {}
    
    quote_elements = soup.find_all('div', class_='quote-info')
    
    for quote_element in quote_elements:
        carrier_name_element = quote_element.find('div', class_='name')
        if not carrier_name_element:
            continue
            
        carrier_name = carrier_name_element.get_text(strip=True)
        
        monthly_element = quote_element.find('div', class_='monthly')
        monthly_span = monthly_element.find('span') if monthly_element else None
        monthly_premium = monthly_span.get_text(strip=True) if monthly_span else None
        
        annual_element = quote_element.find('div', class_='annual')
        annual_span = annual_element.find('span') if annual_element else None
        annual_premium = annual_span.get_text(strip=True) if annual_span else None
        
        carrier_key = clean_carrier_name(carrier_name)
        
        monthly_clean = clean_premium_value(monthly_premium)
        annual_clean = clean_premium_value(annual_premium)
        
        quotes_dict[carrier_key] = {
            "monthly": monthly_clean,
            "annually": annual_clean,
            "original_name": carrier_name
        }
    
    return quotes_dict

def clean_carrier_name(name):
    """
    Convert carrier name to snake_case format for dictionary key.
    
    Args:
        name (str): Original carrier name
        
    Returns:
        str: Cleaned name in snake_case
    """
    if not name:
        return "unknown"
    
    cleaned = re.sub(r'[^\w\s]', '', name.lower())
    cleaned = re.sub(r'\s+', '_', cleaned.strip())
    
    name_mappings = {
        'square_one_insurance_services': 'square_one',
        'sgi_canada': 'sgi_canada',
        'gore': 'gore',
        'pembridge': 'pembridge',
        'economical_mutual': 'economical_mutual'
    }
    
    return name_mappings.get(cleaned, cleaned)

def clean_premium_value(premium_str):
    """
    Clean premium string and convert to float.
    
    Args:
        premium_str (str): Premium string like "$315.16" or "$1,223.58"
        
    Returns:
        float: Cleaned premium as float, or None if invalid
    """
    if not premium_str:
        return None
    
    cleaned = re.sub(r'[$,\s]', '', premium_str)
    
    try:
        return float(cleaned)
    except ValueError:
        return None

def extract_property_details(html_content):
    """
    Extract property details from HTML.
    
    Args:
        html_content (str): HTML content containing property details
        
    Returns:
        dict: Dictionary with property details
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    details = {}
    
    details_pane = soup.find('div', class_='details-pane')
    if not details_pane:
        return details
    
    detail_elements = details_pane.find_all('div', class_='detail')
    
    for detail in detail_elements:
        spans = detail.find_all('span')
        if len(spans) >= 2:
            key = spans[0].get_text(strip=True)
            value = spans[1].get_text(strip=True)
            if value:
                details[key] = value
    
    return details

def extract_complete_data(html_content):
    """
    Extract both quotes and property details from HTML.
    
    Args:
        html_content (str): HTML content
        
    Returns:
        dict: Complete data structure with quotes and property details
    """
    quotes = extract_insurance_quotes(html_content)
    property_details = extract_property_details(html_content)
    
    return {
        "quotes": quotes,
        "property_details": property_details,
        "summary": {
            "total_quotes": len(quotes),
            "best_quote": min(quotes.items(), key=lambda x: x[1]["annually"] or float('inf')) if quotes else None
        }
    }


if __name__ == "__main__":
    with open("final_page.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    
    quotes = extract_insurance_quotes(html_content)
    print(quotes)
    print("Insurance Quotes:")
    for carrier, data in quotes.items():
        print(f"{carrier}: monthly = ${data['monthly']}, annually = ${data['annually']}")
    
    complete_data = extract_complete_data(html_content)
