import csv
import os
import time
import uuid
from datetime import datetime
from typing import Any, Dict

from playwright.sync_api import Playwright


class InsuranceQuoteBot:
    def __init__(
            self, 
            playwright: Playwright, 
            website: str, 
            data: dict, 
            verbose: bool = False,
            screenshots: bool = False,
        ):
        self.playwright = playwright
        self.website = website
        self.data = data
        self.browser = None
        self.page = None
        self.verbose = verbose
        self.screenshots = screenshots
        self.screenshot_counter = 0
        
    def setup(self):
        """Initialize browser and page"""
        self.browser = self.playwright.chromium.launch()
        self.page = self.browser.new_page()
        self.page.goto(self.website)
        
    def teardown(self):
        """Clean up resources"""
        if self.browser:
            self.browser.close()
            
    def wait_for_network_idle(self, timeout: int = 100):
        """Wait for network to be idle"""
        try:
            self.page.wait_for_load_state('networkidle', timeout=timeout)
        except Exception:
            print("Timeout waiting for networkidle, continuing anyway.")
            
    def take_screenshot(self, description: str):
        """Take a screenshot if verbose mode is enabled"""
        if self.screenshots:
            self.screenshot_counter += 1
            os.makedirs("ss", exist_ok=True)
            self.page.screenshot(path=f"ss/{self.screenshot_counter:02d}_{description}.png")
            
    def is_element_readonly(self, element) -> bool:
        """Check if an element is readonly"""
        try:
            return element.get_attribute("readonly") is not None
        except Exception:
            return False
            
    def click_element(self, selector: str, description: str) -> bool:
        """Click an element if it exists"""
        element = self.page.query_selector(selector)
        if element:
            element.click()
            self.wait_for_network_idle()
            self.take_screenshot(f"after_{description}")
            return True
        print(f"Could not find {description} with selector '{selector}'")
        return False
        
    def fill_input(self, selector: str, value: str, description: str) -> bool:
        """Fill an input field if it exists and is not readonly"""
        element = self.page.query_selector(selector)
        if element:
            if self.is_element_readonly(element):
                if self.verbose:
                    print(f"Skipping readonly field: {description}")
                return True
            element.fill(value)
            if self.screenshots:
                self.take_screenshot(f"after_{description}")
            return True
        print(f"Could not find {description} with selector '{selector}'")
        return False
        
    def select_option(self, selector: str, value: str, description: str) -> bool:
        """Select an option from a dropdown if it exists and is not readonly"""
        element = self.page.query_selector(selector)
        if element:
            if self.is_element_readonly(element):
                if self.verbose:
                    print(f"Skipping readonly field: {description}")
                return True
            element.select_option(value)
            if self.screenshots:
                self.take_screenshot(f"after_{description}")
            return True
        print(f"Could not find {description} with selector '{selector}'")
        return False
        
    def click_radio_button(self, name: str, value: str, description: str) -> bool:
        """Click a radio button if it exists and is not readonly"""
        # Handle radio buttons with or without name attribute
        if name:
            radio_input = self.page.query_selector(f'input[type="radio"][name="{name}"][value="{value}"]')
        else:
            radio_input = self.page.query_selector(f'input[type="radio"][value="{value}"]')
            
        if radio_input:
            if self.is_element_readonly(radio_input):
                if self.verbose:
                    print(f"Skipping readonly field: {description}")
                return True
            label = radio_input.evaluate_handle('node => node.closest("label")')
            if label:
                span = label.query_selector('span')
                if span:
                    span.click()
                    if self.screenshots:
                        self.take_screenshot(f"after_{description}")
                    return True
        print(f"Could not find {description} with value '{value}'")
        return False

    def navigate_path(self, path_config: Dict[str, Any]):
        """Navigate through a configured path"""
        for step in path_config['steps']:
            try:
                action = step['action']
                description = step['description']
                step_id = step['id']
                
                # Skip steps that require data if the data is None
                if action in ['fill', 'select', 'radio'] and 'data_key' in step and not step.get('skip_data_check', False):
                    value = self.data.get(step['data_key'])
                    if value is None:
                        if self.verbose:
                            print(f"\nSkipping step {step_id}: No data available for {step['data_key']}")
                        continue
                
                if self.verbose:
                    print(f"\nExecuting step: {step_id} ({description})")
                
                if action == 'click':
                    if not self.click_element(step['selector'], description):
                        raise Exception(f"Failed to click element with selector: {step['selector']}")
                elif action == 'fill':
                    value = self.data.get(step['data_key'], '')
                    if 'transform' in step:
                        value = step['transform'](value)
                    if not value:
                        if self.verbose:
                            print(f"Skipping step {step_id}: Empty value after transform")
                        continue
                    if not self.fill_input(step['selector'], value, description):
                        raise Exception(f"Failed to fill input with selector: {step['selector']}")
                elif action == 'select':
                    value = self.data.get(step['data_key'], '')
                    if 'transform' in step:
                        value = step['transform'](value)
                    if not value:
                        if self.verbose:
                            print(f"Skipping step {step_id}: Empty value after transform")
                        continue
                    if not self.select_option(step['selector'], value, description):
                        raise Exception(f"Failed to select option with selector: {step['selector']}")
                elif action == 'radio':
                    # For radio buttons, use the fixed value if provided, otherwise use data
                    value = step.get('value')
                    if value is None and 'data_key' in step:
                        value = "1" if self.data.get(step['data_key'], False) else "0"
                    if not self.click_radio_button(step.get('name'), value, description):
                        raise Exception(f"Failed to click radio button with value: {value}")
                
                if step.get('wait', False):
                    if self.verbose:
                        print(f"Waiting {step['wait']} seconds...")
                    time.sleep(step['wait'])
                    
            except Exception as e:
                print(f"\nError in step {step_id}:")
                print(f"Description: {description}")
                print(f"Action: {action}")
                print(f"Error: {str(e)}")
                print("\nCurrent page URL:", self.page.url)
                if self.screenshots:
                    self.take_screenshot(f"error_{step_id}")
                raise Exception(f"Failed at step {step_id}: {str(e)}")

    def save_quotes_to_csv(self, quotes: Dict[str, Any], csv_filename: str = "output/sample_data.csv"):
        """Save quotes to CSV file"""
        os.makedirs("output", exist_ok=True)
        file_exists = os.path.isfile(csv_filename)
        
        fieldnames = [
            'id', 'timestamp',
            # Input data fields
            'insurance_type', 'postal_code', 'address', 'unit_apt', 'city',
            'province', 'name', 'date_of_birth', 'move_in_year', 'occupants',
            'active_home_insurance', 'ever_insured', 'num_claims',
            'num_cancellations', 'multiline_discount', 'has_monitored_fire_alarm',
            'has_deadbolt_locks', 'has_monitored_burglar_alarm',
            'has_sprinkler_system', 'occupants_non_smokers',
            'num_fire_extinguishers', 'num_mortgages', 'email', 'phone',
            # Quote result fields
            'carrier_name', 'carrier_original_name', 'monthly_premium',
            'annual_premium'
        ]
        
        with open(csv_filename, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            for carrier, quote_data in quotes.items():
                row = {
                    'id': str(uuid.uuid4()),
                    'timestamp': datetime.now().strftime("%Y%m%d_%H%M%S"),
                    # Input data
                    'insurance_type': self.data.get('insurance_type', ''),
                    'postal_code': self.data.get('postal_code', ''),
                    'address': self.data.get('address', ''),
                    'unit_apt': self.data.get('unit/apt', ''),
                    'city': self.data.get('city', ''),
                    'province': self.data.get('province', ''),
                    'name': self.data.get('name', ''),
                    'date_of_birth': self.data.get('date_of_birth', ''),
                    'move_in_year': self.data.get('move_in_year', ''),
                    'occupants': self.data.get('occupants', ''),
                    'active_home_insurance': self.data.get('active_home_insurance', ''),
                    'ever_insured': self.data.get('ever_insured', ''),
                    'num_claims': self.data.get('num_claims', ''),
                    'num_cancellations': self.data.get('num_cancellations', ''),
                    'multiline_discount': self.data.get('multiline_discount', ''),
                    'has_monitored_fire_alarm': self.data.get('has_monitored_fire_alarm', ''),
                    'has_deadbolt_locks': self.data.get('has_deadbolt_locks', ''),
                    'has_monitored_burglar_alarm': self.data.get('has_monitored_burglar_alarm', ''),
                    'has_sprinkler_system': self.data.get('has_sprinkler_system', ''),
                    'occupants_non_smokers': self.data.get('occupants_non_smokers', ''),
                    'num_fire_extinguishers': self.data.get('num_fire_extinguishers', ''),
                    'num_mortgages': self.data.get('num_mortgages', ''),
                    'email': self.data.get('email', ''),
                    'phone': self.data.get('phone', ''),
                    # Quote data
                    'carrier_name': carrier,
                    'carrier_original_name': quote_data.get('original_name', ''),
                    'monthly_premium': quote_data.get('monthly', ''),
                    'annual_premium': quote_data.get('annually', '')
                }
                writer.writerow(row)
