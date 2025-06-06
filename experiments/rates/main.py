from playwright.sync_api import Playwright, sync_playwright

from ratebot.bot import InsuranceQuoteBot
from ratebot.config import HOME_INSURANCE_PATH
from data.sample import home_profile
from ratebot.utils import extract_insurance_quotes


def run(
        playwright: Playwright, 
        website: str, 
        data: dict, 
        verbose: bool = False,
        screenshots: bool = False,
    ):
    """Run the insurance quote bot."""
    bot = InsuranceQuoteBot(playwright, website, data, verbose, screenshots)
    try:
        bot.setup()
        
        # Navigate through the configured path
        bot.navigate_path(HOME_INSURANCE_PATH)
        
        # Extract and save quotes
        quotes = extract_insurance_quotes(bot.page.content())
        
        if verbose:
            for carrier, quote_data in quotes.items():
                print(f"{carrier}: monthly = ${quote_data['monthly']}, annually = ${quote_data['annually']}")
            
        bot.save_quotes_to_csv(quotes)
        
    finally:
        bot.teardown()


if __name__ == "__main__":
    website = "https://www.rates.ca/"
    with sync_playwright() as playwright:
        run(
            playwright, 
            website, 
            data=home_profile, 
            verbose=True, 
            screenshots=False
        )