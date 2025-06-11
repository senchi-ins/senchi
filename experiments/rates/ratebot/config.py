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
            'wait': 5
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
            'wait': 5
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
            'wait': 5
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
            'description': 'occupants select',
            'wait': 5
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
        # If there were claims, enter the dates
        {
            'id': 'claim_one_month_select',
            'action': 'select',
            'selector': 'select[name="claim-month[0]"]',
            'data_key': 'claim_month_zero',
            'description': 'claim date select'
        },
        {
            'id': 'claim_one_year_select',
            'action': 'select',
            'selector': 'select[name="claim-year[0]"]',
            'data_key': 'claim_year_zero',
            'description': 'claim year select'
        },
        # Enter the claim type
        {
            'id': 'claim_one_type_select',
            'action': 'select',
            'selector': 'select[name="claim-type[0]"]',
            'data_key': 'claim_type_zero',
            'description': 'claim type select'
        },
        # If there was a second claim, enter the dates
        {
            'id': 'claim_two_month_select',
            'action': 'select',
            'selector': 'select[name="claim-month[1]"]',
            'data_key': 'claim_month_one',
            'description': 'claim date select'
        },
        {
            'id': 'claim_two_year_select',
            'action': 'select',
            'selector': 'select[name="claim-year[1]"]',
            'data_key': 'claim_year_one',
            'description': 'claim year select'
        },
        # Enter the claim type
        {
            'id': 'claim_two_type_select',
            'action': 'select',
            'selector': 'select[name="claim-type[1]"]',
            'data_key': 'claim_type_one',
            'description': 'claim type select'
        },
        {
            'id': 'num_cancellations_select',
            'action': 'select',
            'selector': 'select[name="num-cancellations"]',
            'data_key': 'num_cancellations',
            'description': 'number of cancellations select'
        },
        # Select the calcellation month
        {
            'id': 'cancellation_month_select',
            'action': 'select',
            'selector': 'select[name="cancellation-month"]',
            'data_key': 'cancellation_month',
            'description': 'cancellation month select'
        },
        # Select the cancellation year
        {
            'id': 'cancellation_year_select',
            'action': 'select',
            'selector': 'select[name="cancellation-year"]',
            'data_key': 'cancellation_year',
            'description': 'cancellation year select'
        },
        {
            'id': 'submit_button_1',
            'action': 'click',
            'selector': 'button[type="submit"].has-spinner',
            'description': 'submit button',
            'wait': 5
        },
        # Additional property information
        {
            'id': 'nearest_firehall_select',
            'action': 'select',
            'selector': 'select[name="firehall-distance"]',
            'data_key': 'nearest_firehall',
            'description': 'approx distance to nearest fire station select'
        },
        # Nearest firehydrant
        {
            'id': 'nearest_firehydrant_select',
            'action': 'select',
            'selector': 'select[name="hydrants-distance"]',
            'data_key': 'nearest_firehydrant',
            'description': 'approx distance to nearest fire hydrant select'
        },
        # Primary heating
        {
            'id': 'primary_heating_select',
            'action': 'select',
            'selector': 'select[name="primary-heating-type"]',
            'data_key': 'primary_heating',
            'description': 'primary heating select'
        },
        # Click the submit button
        {
            'id': 'submit_button_2',
            'action': 'click',
            'selector': 'button[type="submit"].has-spinner',
            'description': 'submit button',
            'wait': 5
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
            'wait': 5
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
            'wait': 150
        },
        # If quotes don't load, click the link to reload
        {
            'id': 'reload_quotes_link',
            'action': 'click',
            'selector': 'a[href="?noquote"]',
            'description': 'click here if quotes dont load',
            'optional': True,
            'wait': 150
        }
    ]
}
