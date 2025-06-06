"""Navigation configuration for the insurance quote bot."""

HOME_INSURANCE_PATH = {
    'steps': [
        # Initial home insurance selection
        {
            'id': 'home_insurance_icon',
            'action': 'click',
            'selector': 'div.insurance-search-icons-insurance-cta-block-home',
            'description': 'home insurance icon'
        },
        {
            'id': 'insurance_type_select',
            'action': 'select',
            'selector': 'select#insurance-type-select',
            'data_key': 'insurance_type',
            'description': 'insurance type select'
        },
        {
            'id': 'postal_code_input',
            'action': 'fill',
            'selector': 'input[name="postal_code"]',
            'data_key': 'postal_code',
            'description': 'postal code input'
        },
        {
            'id': 'get_quote_button',
            'action': 'click',
            'selector': 'button[type="submit"]#submitBtn',
            'description': 'get my quote button',
            'wait': 30
        },
        
        # Address information
        {
            'id': 'full_address_input',
            'action': 'fill',
            'selector': 'input[name="full-address"]',
            'data_key': 'address',
            'description': 'full address input'
        },
        {
            'id': 'continue_button_1',
            'action': 'click',
            'selector': 'button[name="submit"]#continue-button',
            'description': 'continue button',
            'wait': 30
        },
        {
            'id': 'street_address_input',
            'action': 'fill',
            'selector': 'input[name="street-address"]',
            'data_key': 'address',
            'description': 'street address input'
        },
        {
            'id': 'unit_apt_input',
            'action': 'fill',
            'selector': 'input[name="unit"]',
            'data_key': 'unit/apt',
            'description': 'unit/apt input'
        },
        {
            'id': 'city_input',
            'action': 'fill',
            'selector': 'input[name="city"]',
            'data_key': 'city',
            'description': 'city input'
        },
        {
            'id': 'postal_code_input_2',
            'action': 'fill',
            'selector': 'input[name="postal-code"]',
            'data_key': 'postal_code',
            'description': 'postal code input'
        },
        {
            'id': 'province_input',
            'action': 'fill',
            'selector': 'input[name="province"]',
            'data_key': 'province',
            'description': 'province input'
        },
        {
            'id': 'continue_button_2',
            'action': 'click',
            'selector': 'button[name="submit"]#continue-button',
            'description': 'continue button',
            'wait': 30
        },
        
        # Personal information
        {
            'id': 'first_name_input',
            'action': 'fill',
            'selector': 'input[name="first-name"]',
            'data_key': 'name',
            'description': 'first name input',
            'transform': lambda x: x.split(" ")[0] if x else ""
        },
        {
            'id': 'last_name_input',
            'action': 'fill',
            'selector': 'input[name="last-name"]',
            'data_key': 'name',
            'description': 'last name input',
            'transform': lambda x: x.split(" ")[1] if x and len(x.split(" ")) > 1 else ""
        },
        {
            'id': 'dob_month_select',
            'action': 'select',
            'selector': 'select[name="dob-month"]',
            'data_key': 'date_of_birth',
            'description': 'month of birth select',
            'transform': lambda x: str(int(x.split("-")[1])) if x and len(x.split("-")) > 1 else ""
        },
        {
            'id': 'dob_day_select',
            'action': 'select',
            'selector': 'select[name="dob-day"]',
            'data_key': 'date_of_birth',
            'description': 'day of birth select',
            'transform': lambda x: str(int(x.split("-")[2])) if x and len(x.split("-")) > 2 else ""
        },
        {
            'id': 'dob_year_select',
            'action': 'select',
            'selector': 'select[name="dob-year"]',
            'data_key': 'date_of_birth',
            'description': 'year of birth select',
            'transform': lambda x: x.split("-")[0] if x else ""
        },
        {
            'id': 'move_in_year_select',
            'action': 'select',
            'selector': 'select[name="occupation-year"]',
            'data_key': 'move_in_year',
            'description': 'move in year select'
        },
        {
            'id': 'occupants_select',
            'action': 'select',
            'selector': 'select[name="num-families"]',
            'data_key': 'occupants',
            'description': 'occupants select'
        },
        
        # Insurance history
        {
            'id': 'active_insurance_radio',
            'action': 'radio',
            'name': 'is-insured',
            'data_key': 'active_home_insurance',
            'description': 'active home insurance radio'
        },
        {
            'id': 'ever_insured_radio',
            'action': 'radio',
            'name': 'was-insured',
            'data_key': 'ever_insured',
            'description': 'ever insured radio'
        },
        {
            'id': 'num_claims_select',
            'action': 'select',
            'selector': 'select[name="num-claims"]',
            'data_key': 'num_claims',
            'description': 'number of claims select'
        },
        {
            'id': 'num_cancellations_select',
            'action': 'select',
            'selector': 'select[name="num-cancellations"]',
            'data_key': 'num_cancellations',
            'description': 'number of cancellations select'
        },
        {
            'id': 'submit_button_1',
            'action': 'click',
            'selector': 'button[type="submit"].has-spinner',
            'description': 'submit button',
            'wait': 30
        },
        
        # Discounts
        {
            'id': 'multiline_discount_radio',
            'action': 'radio',
            'name': 'has-multiline',
            'data_key': 'multiline_discount',
            'description': 'multiline discount radio'
        },
        {
            'id': 'fire_alarm_radio',
            'action': 'radio',
            'name': 'has-fire-alarm',
            'data_key': 'has_monitored_fire_alarm',
            'description': 'monitored fire alarm radio'
        },
        {
            'id': 'deadbolt_locks_radio',
            'action': 'radio',
            'name': 'has-deadbolt-locks',
            'data_key': 'has_deadbolt_locks',
            'description': 'deadbolt locks radio'
        },
        {
            'id': 'burglar_alarm_radio',
            'action': 'radio',
            'name': 'has-burglar-alarm',
            'data_key': 'has_monitored_burglar_alarm',
            'description': 'monitored burglar alarm radio'
        },
        {
            'id': 'sprinkler_system_radio',
            'action': 'radio',
            'name': 'has-sprinkler-system',
            'data_key': 'has_sprinkler_system',
            'description': 'sprinkler system radio'
        },
        {
            'id': 'non_smokers_radio',
            'action': 'radio',
            'name': 'is-non-smoker',
            'data_key': 'occupants_non_smokers',
            'description': 'non-smokers radio'
        },
        {
            'id': 'fire_extinguishers_select',
            'action': 'select',
            'selector': 'select[name="num-fire-extinguishers"]',
            'data_key': 'num_fire_extinguishers',
            'description': 'number of fire extinguishers select'
        },
        {
            'id': 'mortgages_select',
            'action': 'select',
            'selector': 'select[name="num-mortgages"]',
            'data_key': 'num_mortgages',
            'description': 'number of mortgages select'
        },
        
        # Contact information
        {
            'id': 'email_input',
            'action': 'fill',
            'selector': 'input[name="email"]',
            'data_key': 'email',
            'description': 'email input'
        },
        {
            'id': 'phone_input',
            'action': 'fill',
            'selector': 'input[name="phone"]',
            'data_key': 'phone',
            'description': 'phone input'
        },
        {
            'id': 'signup_checkbox',
            'action': 'click',
            'selector': 'label[for="signup-weekly-mandatory"]',
            'description': 'signup checkbox'
        },
        {
            'id': 'discount_form_submit',
            'action': 'click',
            'selector': 'button[type="submit"]#discount-form-submit',
            'description': 'discount form submit button',
            'wait': 30
        },
        # Final steps
        {
            'id': 'no_credit_check_radio',
            'action': 'radio',
            'value': '0',
            'description': 'no credit check radio',
            'skip_data_check': True  # Skip data_key check since we're using a fixed value
        },
        {
            'id': 'final_submit_button',
            'action': 'click',
            'selector': 'button[name="action"]',
            'description': 'final submit button',
            'wait': 50  # Wait for quotes to load
        }
    ]
}

nav = {
    "auto": {
        "vehicle_year": "select[name='vehicle-year[]']",
    },
    "home": {
        "tab_name": "insurance-search-icons-insurance-cta-block-home",
        "year": "select[name='home-year[]']",
    },
}