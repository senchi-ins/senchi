from time import sleep

import pandas as pd
from tqdm import tqdm
from playwright.sync_api import Playwright, sync_playwright

from ratebot.bot import InsuranceQuoteBot
from ratebot.config import HOME_INSURANCE_PATH
from ratebot.cleaning import clean_data

from ratebot.utils import extract_insurance_quotes, row_to_dict

CHECKPOINT_INDEX = 54

def run(
        playwright: Playwright, 
        website: str, 
        data: pd.DataFrame,
        max_retries: int = 3,
        sleep_time: int = 10,
        verbose: bool = False,
        screenshots: bool = False,
        headless: bool = True,
    ):
    """Run the insurance quote bot."""
    bot = InsuranceQuoteBot(
        playwright=playwright, 
        website=website, 
        max_retries=max_retries,
        verbose=verbose, 
        screenshots=screenshots, 
        headless=headless
    )
    try:
        for idx, row in tqdm(data.iterrows(), total=len(data)):
            if idx < CHECKPOINT_INDEX:
                continue
            
            bot.setup()
            row = row_to_dict(row)

            check = False
            retry_count = 0
            try:
                while not check and retry_count < max_retries:
                    bot.navigate_path(HOME_INSURANCE_PATH, row)
            
                    quotes = extract_insurance_quotes(bot.page.content())
                    if quotes:
                        check = True
                    else:
                        retry_count += 1
                        sleep(sleep_time)
                    
                    if verbose:
                        for carrier, quote_data in quotes.items():
                            print(f"{carrier}: monthly = ${quote_data['monthly']}, annually = ${quote_data['annually']}")
                        
                    # Results may need to be chunked, saving into multiple files to avoid loss
                    bot.save_quotes_to_csv(quotes, row, csv_filename=f"output/sample_data_{CHECKPOINT_INDEX}.csv")
                    print(f"Saved quotes for {row['name']} to output/sample_data.csv")
                    sleep(sleep_time)
            except Exception as e:
                print(f"Error: {e}")
                sleep(sleep_time)
                continue
        
    finally:
        bot.teardown()


if __name__ == "__main__":
    website = "https://www.rates.ca/"
    # data = pd.read_csv("data/Insurance_Dataset.csv")
    data = pd.read_csv("data/sm_insurance_dataset.csv")
    
    data = clean_data(data)
    
    with sync_playwright() as playwright:
        run(
            playwright, 
            website, 
            data=data,
            max_retries=1,
            verbose=True, 
            screenshots=False,
            headless=True,
        )