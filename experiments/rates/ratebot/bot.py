import os
import time
import uuid
from datetime import datetime
from typing import Any, Dict

import pandas as pd
from playwright.sync_api import Playwright


class InsuranceQuoteBot:
    def __init__(
            self, 
            playwright: Playwright, 
            website: str, 
            max_retries: int = 3,
            verbose: bool = False,
            screenshots: bool = False,
            headless: bool = True,
        ):
        self.playwright = playwright
        self.website = website
        self.max_retries = max_retries
        self.browser = None
        self.page = None
        self.verbose = verbose
        self.screenshots = screenshots
        self.screenshot_counter = 0
        self.data = None  # Store the current data being processed
        self.headless = headless

    def setup(self):
        """Initialize browser and page"""
        self.browser = self.playwright.chromium.launch(headless=self.headless)
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
        self.take_screenshot(f"error_{description}")
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
            str_value = str(value) if pd.notna(value) and value != "" else ""
            element.fill(str_value)
            if self.screenshots:
                self.take_screenshot(f"after_{description}")
            return True
        print(f"Could not find {description} with selector '{selector}'")
        return False
        
    def select_option(self, selector: str, value: str, description: str) -> bool:
        """Select an option from a dropdown if it exists and is not readonly"""
        max_retries = self.max_retries
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                element = self.page.query_selector(selector)
                if element:
                    if self.is_element_readonly(element):
                        if self.verbose:
                            print(f"Skipping readonly field: {description}")
                        return True
                    # Convert value to string if it's numeric
                    str_value = str(value) if pd.notna(value) else ""
                    element.select_option(str_value)
                    if self.screenshots:
                        self.take_screenshot(f"after_{description}")
                    return True
                    
                if attempt < max_retries - 1:
                    if self.verbose:
                        print(f"Retry {attempt + 1}/{max_retries} for {description}")
                    time.sleep(retry_delay)
                    continue
                    
                print(f"Could not find {description} with selector '{selector}'")
                return False
                
            except Exception as e:
                if attempt < max_retries - 1:
                    if self.verbose:
                        print(f"Error selecting option: {str(e)}")
                        print(f"Retry {attempt + 1}/{max_retries} for {description}")
                    time.sleep(retry_delay)
                    continue
                raise
        
    def click_radio_button(self, name: str, value: str, description: str) -> bool:
        """Click a radio button if it exists and is not readonly"""
        # Convert boolean values to "1" or "0"
        if isinstance(value, bool):
            value = "1" if value else "0"
        elif pd.notna(value):
            value = str(value)
        else:
            value = "0"  # Default to "0" for None/NA values
            
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
                
            # Try clicking the radio input directly first
            try:
                radio_input.click()
                if self.screenshots:
                    self.take_screenshot(f"after_{description}")
                return True
            except Exception as e:
                if self.verbose:
                    print(f"Failed to click radio input directly: {str(e)}")
            
            # If direct click fails, try clicking the label
            label = radio_input.evaluate_handle('node => node.closest("label")')
            if label:
                try:
                    label.click()
                    if self.screenshots:
                        self.take_screenshot(f"after_{description}")
                    return True
                except Exception as e:
                    if self.verbose:
                        print(f"Failed to click label: {str(e)}")
                        
                # If label click fails, try clicking the span
                span = label.query_selector('span')
                if span:
                    try:
                        span.click()
                        if self.screenshots:
                            self.take_screenshot(f"after_{description}")
                        return True
                    except Exception as e:
                        if self.verbose:
                            print(f"Failed to click span: {str(e)}")
        
        if self.verbose:
            print(f"Could not find or click {description} with value '{value}'")
            # Print all radio buttons on the page for debugging
            radio_buttons = self.page.query_selector_all('input[type="radio"]')
            print(f"Found {len(radio_buttons)} radio buttons on the page")
            for rb in radio_buttons:
                print(f"Radio button: name={rb.get_attribute('name')}, value={rb.get_attribute('value')}")
                
        return False

    def navigate_path(self, path_config: Dict[str, Any], data: pd.Series):
        """Navigate through a configured path"""
        
        for step in path_config['steps']:
            try:
                action = step['action']
                description = step['description']
                step_id = step['id']
                
                # Skip home insurance icon click if we're already on the home insurance page
                if step_id == 'home_insurance_icon' and 'homequote' in self.page.url:
                    if self.verbose:
                        print(f"\nSkipping step {step_id}: Already on home insurance page")
                    continue
                
                # Skip steps that require data if the data is None
                if action in ['fill', 'select', 'radio'] and 'data_key' in step and not step.get('skip_data_check', False):
                    value = data.get(step['data_key'])
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
                    value = data.get(step['data_key'], '')
                    if 'transform' in step:
                        value = step['transform'](value)
                    if not value:
                        if self.verbose:
                            print(f"Skipping step {step_id}: Empty value after transform")
                        continue
                    if not self.fill_input(step['selector'], value, description):
                        raise Exception(f"Failed to fill input with selector: {step['selector']}")
                elif action == 'select':
                    value = data.get(step['data_key'], '')
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
                        value = "1" if data.get(step['data_key'], False) else "0"
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
                # raise Exception(f"Failed at step {step_id}: {str(e)}")
                continue

    def save_quotes_to_csv(self, quotes: Dict[str, Any], data: Dict[str, Any], csv_filename: str = "output/sample_data.csv"):
        """Save quotes to CSV file using pandas"""
        os.makedirs("output", exist_ok=True)
        
        # Create a list to store all quote rows
        quote_rows = []
        
        # Create base data dictionary from the input data
        base_data = {
            'id': str(uuid.uuid4()),
            'timestamp': datetime.now().strftime("%Y%m%d_%H%M%S"),
            # Input data
            'insurance_type': data.get('insurance_type', ''),
            'postal_code': data.get('postal_code', ''),
            'address': data.get('address', ''),
            'unit_apt': data.get('unit_apt', ''),
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
        }
        
        # Add quote data for each carrier
        for carrier, quote_data in quotes.items():
            row = base_data.copy()
            row.update({
                'carrier_name': carrier,
                'carrier_original_name': quote_data.get('original_name', ''),
                'monthly_premium': quote_data.get('monthly', ''),
                'annual_premium': quote_data.get('annually', '')
            })
            quote_rows.append(row)
        
        # Create DataFrame from the rows
        df = pd.DataFrame(quote_rows)
        
        # Save to CSV
        if os.path.exists(csv_filename):
            # Append without header if file exists
            df.to_csv(csv_filename, mode='a', header=False, index=False)
        else:
            # Write with header if file doesn't exist
            df.to_csv(csv_filename, index=False)
            
        if self.verbose:
            print(f"Saved {len(quote_rows)} quotes to {csv_filename}")
