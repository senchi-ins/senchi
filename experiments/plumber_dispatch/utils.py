
def format_phone_number(phone_number: str) -> str:
    phone_number = phone_number.replace(" ", "").replace("-", "")
    return phone_number