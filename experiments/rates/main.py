from playwright.sync_api import sync_playwright, Playwright
import time
from data.sample import home_profile
from config import nav
from helper import extract_insurance_quotes
import csv
import uuid
from datetime import datetime
import os

def run(playwright: Playwright, website: str, data: dict = home_profile):
    chromium = playwright.chromium
    browser = chromium.launch()
    page = browser.new_page()
    page.goto(website)

    # Find and click the div with the specific class name
    home_icon = page.query_selector('div.insurance-search-icons-insurance-cta-block-home')
    if home_icon:
        home_icon.click()
        try:
            page.wait_for_load_state('networkidle', timeout=10000)
        except Exception:
            print("Timeout waiting for networkidle, continuing anyway.")
        # page.screenshot(path="ss/1_after_home_icon_click.png")
    else:
        print("Could not find the div with class 'insurance-search-icons-insurance-cta-block-home'.")

    # Find the <select> with id 'insurance-type-select'
    select_elem = page.query_selector('select#insurance-type-select')
    if select_elem:
        # Select the option matching the insurance type from your data
        insurance_type = data["insurance_type"]
        select_elem.select_option("H")
        # page.screenshot(path="ss/2_after_insurance_type_select.png")
    else:
        print("Could not find the select element with id 'insurance-type-select'.")

    # Find the postal code input, 
    postal_code_input = page.query_selector('input[name="postal_code"]')
    if postal_code_input:
        postal_code_input.fill(data["postal_code"])
        # page.screenshot(path="ss/3_after_postal_code_input.png")
    else:
        print("Could not find the postal code input.")

    # Click the get my quote button
    get_my_quote_button = page.query_selector('button[type="submit"]#submitBtn')
    if get_my_quote_button:
        get_my_quote_button.click()
        try:
            page.wait_for_load_state('networkidle', timeout=10000)
        except Exception:
            print("Timeout waiting for networkidle, continuing anyway.")
        # page.screenshot(path="ss/4_after_get_my_quote_button_click.png")
    else:
        print("Could not find the get my quote button.")


    # Find the address input
    address_input = page.query_selector('input[name="full-address"]')
    if address_input:
        address_input.fill(data["address"])
        # page.screenshot(path="ss/5_after_address_input.png")
    else:
        print("Could not find the address input.")

    # Click the submit button
    submit_button = page.query_selector('button[name="submit"]#continue-button')
    if submit_button:
        submit_button.click()
        try:
            page.wait_for_load_state('networkidle', timeout=10000)
        except Exception:
            print("Timeout waiting for networkidle, continuing anyway.")
        time.sleep(2)
        # page.screenshot(path="ss/6_after_submit_button_click.png")
    else:
        print("Could not find the submit button.")

    # If the address isn't populated, fill it in
    # Find the address input which has the name "street-address"
    street_address_input = page.query_selector('input[name="street-address"]')
    if street_address_input:
        street_address_input.fill(data["address"])
        # page.screenshot(path="ss/7_after_street_address_input.png")
    else:
        print("Could not find the street address input.")

    # Find the unit/apt input if it exists in the data passed in
    unit_apt_input = page.query_selector('input[name="unit"]')
    if unit_apt_input and data["unit/apt"]:
        unit_apt_input.fill(data["unit/apt"])
        # page.screenshot(path="ss/7_after_unit_apt_input.png")
    else:
        print("Could not find the unit/apt input.")

    # Find the address input which has the name "city"
    city_input = page.query_selector('input[name="city"]')
    if city_input:
        city_input.fill(data["city"])
        # page.screenshot(path="ss/8_after_city_input.png")
    else:
        print("Could not find the city input.")

    # Fill in the postal code input
    postal_code_input = page.query_selector('input[name="postal-code"]')
    if postal_code_input:
        postal_code_input.fill(data["postal_code"])
        # page.screenshot(path="ss/9_after_postal_code_input.png")
    else:
        print("Could not find the postal code input.")

    # Find the province input
    province_input = page.query_selector('input[name="province"]')
    if province_input:
        is_readonly = province_input.get_attribute("readonly") is not None
        if not is_readonly:
            province_input.fill(data["province"])
            # page.screenshot(path="ss/10_after_province_input.png")
        else:
            print("Province input is read-only, skipping fill.")
    else:
        print("Could not find the province input.")

    # TODO: Extract this into its own function
    submit_button = page.query_selector('button[name="submit"]#continue-button')
    if submit_button:
        submit_button.click()
        try:
            page.wait_for_load_state('networkidle', timeout=10000)
        except Exception:
            print("Timeout waiting for networkidle, continuing anyway.")
        time.sleep(2)
        # page.screenshot(path="ss/10_after_submit_button_click.png")
    else:
        print("Could not find the submit button.")

    # Input the first name
    first_name_input = page.query_selector('input[name="first-name"]')
    if first_name_input:
        first_name_input.fill(data["name"].split(" ")[0])
        # page.screenshot(path="ss/11_after_first_name_input.png")
    else:
        print("Could not find the first name input.")

    # Input the last name
    last_name_input = page.query_selector('input[name="last-name"]')
    if last_name_input:
        last_name_input.fill(data["name"].split(" ")[1])
        # page.screenshot(path="ss/12_after_last_name_input.png")
    else:
        print("Could not find the last name input.")

    # Select the month of birth
    month_select = page.query_selector('select[name="dob-month"]')
    if month_select:
        # Extract the month as an integer (removing leading zero)
        month_value = str(int(data["date_of_birth"].split("-")[1]))
        month_select.select_option(month_value)
        # page.screenshot(path="ss/13_after_month_of_birth_input.png")
    else:
        print("Could not find the month of birth input.")

    day_select = page.query_selector('select[name="dob-day"]')
    if day_select:
        # Extract the day as an integer (removing leading zero)
        day_value = str(int(data["date_of_birth"].split("-")[1]))
        day_select.select_option(day_value)
        # page.screenshot(path="ss/14_after_day_of_birth_input.png")
    else:
        print("Could not find the day of birth input.")

    # Select the year of birth
    year_select = page.query_selector('select[name="dob-year"]')
    if year_select:
        year_select.select_option(data["date_of_birth"].split("-")[0])
        # page.screenshot(path="ss/15_after_year_of_birth_input.png")
    else:
        print("Could not find the year of birth input.")

    # Select the move in year
    move_in_year_select = page.query_selector('select[name="occupation-year"]')
    if move_in_year_select:
        move_in_year_select.select_option(data["move_in_year"])
        # page.screenshot(path="ss/16_after_move_in_year_input.png")
    else:
        print("Could not find the move in year input.")

    # Select the occupants
    occupants_select = page.query_selector('select[name="num-families"]')
    if occupants_select:
        occupants_select.select_option(data["occupants"])
        # page.screenshot(path="ss/17_after_occupants_input.png")
    else:
        print("Could not find the occupants input.")

    # Select the radio button for active home insurance by clicking the span inside the label
    insurance_value = "1" if data["active_home_insurance"] else "0"
    radio_input = page.query_selector(f'input[name="is-insured"][value="{insurance_value}"]')
    if radio_input:
        label = radio_input.evaluate_handle('node => node.closest("label")')
        if label:
            span = label.query_selector('span')
            if span:
                span.click()
                # page.screenshot(path="ss/18_after_is_insured_input.png")
            else:
                print(f'Could not find the span inside the label for is-insured with value {insurance_value}.')
        else:
            print(f'Could not find the label for is-insured with value {insurance_value}.')
    else:
        print(f'Could not find the radio button for is-insured with value {insurance_value}.')

    # Select the ever insured radio button
    ever_insured_value = "1" if data["ever_insured"] else "0"
    ever_insured_radio_input = page.query_selector(f'input[name="was-insured"][value="{ever_insured_value}"]')
    if ever_insured_radio_input:
        label = ever_insured_radio_input.evaluate_handle('node => node.closest("label")')
        if label:
            span = label.query_selector('span')
            if span:
                span.click()
                # page.screenshot(path="ss/19_after_ever_insured_input.png")
            else:
                print(f'Could not find the span inside the label for ever-insured with value {ever_insured_value}.')
        else:
            print(f'Could not find the label for ever-insured with value {ever_insured_value}.')

    # Select the number of claims for the past 5 years
    num_claims = page.query_selector('select[name="num-claims"]')
    if num_claims:
        num_claims.select_option(data["num_claims"])
        # page.screenshot(path="ss/20_after_num_claims_input.png")
    else:
        print("Could not find the num-claims input.")

    num_claims = page.query_selector('select[name="num-cancellations"]')
    if num_claims:
        num_claims.select_option(data["num_cancellations"])
        # page.screenshot(path="ss/20_after_move_in_year_input.png")
    else:
        print("Could not find the move in year input.")


    submit_button = page.query_selector('button[type="submit"].has-spinner')
    if submit_button:
        with page.expect_navigation():
            submit_button.click()
        try:
            page.wait_for_load_state('networkidle', timeout=10000)
        except Exception:
            print("Timeout waiting for networkidle, continuing anyway.")
        time.sleep(2)
        # page.screenshot(path="ss/21_after_submit_button_click.png")
    else:
        print("Could not find the submit button.")

    # Go through the discounts that are available
    multiline = "1" if data["multiline_discount"] else "0"
    multiline_input = page.query_selector(f'input[name="has-multiline"][value="{multiline}"]')
    if multiline_input:
        label = multiline_input.evaluate_handle('node => node.closest("label")')
        if label:
            span = label.query_selector('span')
            if span:
                span.click()
                # page.screenshot(path="ss/22_after_ever_insured_input.png")
            else:
                print(f'Could not find the span inside the label for has-multiline with value {multiline}.')
        else:
            print(f'Could not find the label for has-multiline with value {multiline}.')


    has_monitored_fire_alarm = "1" if data["has_monitored_fire_alarm"] else "0"
    has_monitored_fire_alarm_input = page.query_selector(f'input[name="has-fire-alarm"][value="{has_monitored_fire_alarm}"]')
    if has_monitored_fire_alarm_input:
        label = has_monitored_fire_alarm_input.evaluate_handle('node => node.closest("label")')
        if label:
            span = label.query_selector('span')
            if span:
                span.click()
                # page.screenshot(path="ss/23_after_ever_insured_input.png")
            else:
                print(f'Could not find the span inside the label for has-has_monitored_fire_alarm with value {has_monitored_fire_alarm}.')
        else:
            print(f'Could not find the label for has-has_monitored_fire_alarm with value {has_monitored_fire_alarm}.')


    has_deadbolt_locks = "1" if data["has_deadbolt_locks"] else "0"
    has_deadbolt_locks_input = page.query_selector(f'input[name="has-deadbolt-locks"][value="{has_deadbolt_locks}"]')
    if has_deadbolt_locks_input:
        label = has_deadbolt_locks_input.evaluate_handle('node => node.closest("label")')
        if label:
            span = label.query_selector('span')
            if span:
                span.click()
                # page.screenshot(path="ss/24_after_ever_insured_input.png")
            else:
                print(f'Could not find the span inside the label for has-has_deadbolt_locks with value {has_deadbolt_locks}.')
        else:
            print(f'Could not find the label for has-has_deadbolt_locks with value {has_deadbolt_locks}.')


    has_monitored_burglar_alarm = "1" if data["has_monitored_burglar_alarm"] else "0"
    has_monitored_burglar_alarm_input = page.query_selector(f'input[name="has-burglar-alarm"][value="{has_monitored_burglar_alarm}"]')
    if has_monitored_burglar_alarm_input:
        label = has_monitored_burglar_alarm_input.evaluate_handle('node => node.closest("label")')
        if label:
            span = label.query_selector('span')
            if span:
                span.click()
                # page.screenshot(path="ss/25_after_ever_insured_input.png")
            else:
                print(f'Could not find the span inside the label for has-has_monitored_burglar_alarm with value {has_monitored_burglar_alarm}.')
        else:
            print(f'Could not find the label for has-has_monitored_burglar_alarm with value {has_monitored_burglar_alarm}.')

    has_sprinkler_system = "1" if data["has_sprinkler_system"] else "0"
    has_sprinkler_system_input = page.query_selector(f'input[name="has-sprinkler-system"][value="{has_sprinkler_system}"]')
    if has_sprinkler_system_input:
        label = has_sprinkler_system_input.evaluate_handle('node => node.closest("label")')
        if label:
            span = label.query_selector('span')
            if span:
                span.click()
                # page.screenshot(path="ss/26_after_ever_insured_input.png")
            else:
                print(f'Could not find the span inside the label for has-has_sprinkler_system with value {has_sprinkler_system}.')
        else:
            print(f'Could not find the label for has-has_sprinkler_system with value {has_sprinkler_system}.')


    occupants_non_smokers = "1" if data["occupants_non_smokers"] else "0"
    occupants_non_smokers_input = page.query_selector(f'input[name="is-non-smoker"][value="{occupants_non_smokers}"]')
    if occupants_non_smokers_input:
        label = occupants_non_smokers_input.evaluate_handle('node => node.closest("label")')
        if label:
            span = label.query_selector('span')
            if span:
                span.click()
                page.screenshot(path="ss/27_after_ever_insured_input.png")
            else:
                print(f'Could not find the span inside the label for has-has_occupants_non_smokers with value {occupants_non_smokers}.')
        else:
            print(f'Could not find the label for has-has_occupants_non_smokers with value {occupants_non_smokers}.')


    num_fire_extinguishers = page.query_selector('select[name="num-fire-extinguishers"]')
    if num_fire_extinguishers:
        num_fire_extinguishers.select_option(data["num_fire_extinguishers"])
        # page.screenshot(path="ss/28_fter_ever_insured_input.png")
    else:
        print("Could not find the num-fire-extinguishers input.")

    num_mortgages = page.query_selector('select[name="num-mortgages"]')
    if num_mortgages:
        num_mortgages.select_option(data["num_mortgages"])
        # page.screenshot(path="ss/29_fter_ever_insured_input.png")
    else:
        print("Could not find the num-mortgages input.")

    email_input = page.query_selector('input[name="email"]')
    if email_input:
        email_input.fill(data["email"])
        # page.screenshot(path="ss/30_fter_ever_insured_input.png")
    else:
        print("Could not find the email input.")

    phone_input = page.query_selector('input[name="phone"]')
    if phone_input:
        phone_input.fill(data["phone"])
        # page.screenshot(path="ss/31_fter_ever_insured_input.png")
    else:
        print("Could not find the phone input.")

    label = page.query_selector('label[for="signup-weekly-mandatory"]')
    if label:
        label.click()
        # page.screenshot(path="ss/32_after_checkbox_checked.png")
    else:
        print("Could not find the label for the signup weekly mandatory checkbox.")

    submit_button = page.query_selector('button[type="submit"]#discount-form-submit')
    if submit_button:
        with page.expect_navigation():
            submit_button.click()
        try:
            page.wait_for_load_state('networkidle', timeout=10000)
        except Exception:
            print("Timeout waiting for networkidle, continuing anyway.")
        time.sleep(2)
        # page.screenshot(path="ss/33_after_submit_button_click.png")
    else:
        print("Could not find the submit button.")

    # No credit check
    # Click the input button with type "radio" and value "0"
    no_credit_check_input = page.query_selector('input[type="radio"][value="0"]')
    if no_credit_check_input:
        label = no_credit_check_input.evaluate_handle('node => node.closest("label")')
        if label:
            span = label.query_selector('span')
            if span:
                span.click()
                # page.screenshot(path="ss/34_after_no_credit_check_input.png")
            else:
                print(f'Could not find the span inside the label for no-credit-check with value 0.')
        else:
            print(f'Could not find the label for no-credit-check with value 0.')
    else:
        print("Could not find the no credit check input.")

    # Click the final submit button
    submit_button = page.query_selector('button[name="action"]')
    if submit_button:
        with page.expect_navigation():
            submit_button.click()
        try:
            page.wait_for_load_state('networkidle', timeout=10000)
        except Exception:
            print("Timeout waiting for networkidle, continuing anyway.")
        time.sleep(30)
        page.screenshot(path="ss/35_after_final_submit_button_click.png")

    # Extract quotes from the page content
    quotes = extract_insurance_quotes(page.content())
    print("\nInsurance Quotes:")
    for carrier, quote_data in quotes.items():
        print(f"{carrier}: monthly = ${quote_data['monthly']}, annually = ${quote_data['annually']}")

    # Write results to CSV
    csv_filename = "output/sample_data.csv"
    
    # Ensure output directory exists
    os.makedirs("output", exist_ok=True)
    
    # Check if file exists to determine if we need to write headers
    file_exists = os.path.isfile(csv_filename)
    
    with open(csv_filename, 'a', newline='') as csvfile:
        fieldnames = [
            'id',
            'timestamp',
            # Input data fields
            'insurance_type',
            'postal_code',
            'address',
            'unit_apt',
            'city',
            'province',
            'name',
            'date_of_birth',
            'move_in_year',
            'occupants',
            'active_home_insurance',
            'ever_insured',
            'num_claims',
            'num_cancellations',
            'multiline_discount',
            'has_monitored_fire_alarm',
            'has_deadbolt_locks',
            'has_monitored_burglar_alarm',
            'has_sprinkler_system',
            'occupants_non_smokers',
            'num_fire_extinguishers',
            'num_mortgages',
            'email',
            'phone',
            # Quote result fields
            'carrier_name',
            'carrier_original_name',
            'monthly_premium',
            'annual_premium'
        ]
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        # Write a row for each quote
        for carrier, quote_data in quotes.items():
            row = {
                'id': str(uuid.uuid4()),
                'timestamp': datetime.now().strftime("%Y%m%d_%H%M%S"),
                # Input data
                'insurance_type': data.get('insurance_type', ''),
                'postal_code': data.get('postal_code', ''),
                'address': data.get('address', ''),
                'unit_apt': data.get('unit/apt', ''),
                'city': data.get('city', ''),
                'province': data.get('province', ''),
                'name': data.get('name', ''),
                'date_of_birth': data.get('date_of_birth', ''),
                'move_in_year': data.get('move_in_year', ''),
                'occupants': data.get('occupants', ''),
                'active_home_insurance': data.get('active_home_insurance', ''),
                'ever_insured': data.get('ever_insured', ''),
                'num_claims': data.get('num_claims', ''),
                'num_cancellations': data.get('num_cancellations', ''),
                'multiline_discount': data.get('multiline_discount', ''),
                'has_monitored_fire_alarm': data.get('has_monitored_fire_alarm', ''),
                'has_deadbolt_locks': data.get('has_deadbolt_locks', ''),
                'has_monitored_burglar_alarm': data.get('has_monitored_burglar_alarm', ''),
                'has_sprinkler_system': data.get('has_sprinkler_system', ''),
                'occupants_non_smokers': data.get('occupants_non_smokers', ''),
                'num_fire_extinguishers': data.get('num_fire_extinguishers', ''),
                'num_mortgages': data.get('num_mortgages', ''),
                'email': data.get('email', ''),
                'phone': data.get('phone', ''),
                # Quote data
                'carrier_name': carrier,
                'carrier_original_name': quote_data.get('original_name', ''),
                'monthly_premium': quote_data.get('monthly', ''),
                'annual_premium': quote_data.get('annually', '')
            }
            writer.writerow(row)

    browser.close()


if __name__ == "__main__":
    website = "https://www.rates.ca/"
    with sync_playwright() as playwright:
        run(playwright, website)

