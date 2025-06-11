import re
import time
from typing import Optional

from tqdm import tqdm
import pandas as pd
from geopy.geocoders import Nominatim

SLEEP_TIME = 10
MAX_ADDRESSES = 1_000
START_INDEX = 178 # Note: All before got deletedted on refresh, need to re-run with max = 178

def main(
        data_path: str,
        sleep_time: int = SLEEP_TIME, 
        max_addresses: Optional[int] = MAX_ADDRESSES
    ) -> int:
    """
    Main function to populate the postal codes for the addresses.

    Args:
        data_path: Path to the csv file containing the addresses
        sleep_time: Time to sleep between requests to the nominatim server
        max_addresses: Maximum number of addresses to process

    Returns 0 on success, 1 on failure.
    """
    addresses = pd.read_csv(data_path, low_memory=False)
    geoloc = Nominatim(user_agent="openstreetmap")

    addresses = populate_postal_codes(
        geoloc=geoloc,
        addresses=addresses,
        sleep_time=sleep_time,
        max_addresses=max_addresses
    )

    return 0 if addresses is not None else 1


def get_postal_code(
        geoloc: Nominatim, address: str
    ) -> Optional[str]:
    """
    Get the postal code for the address.

    Args:
        geoloc: Geolocator object
        address: Address to get the postal code for
    """
    expr = r'\b[A-Z][0-9][A-Z]\s?[0-9][A-Z][0-9]\b'
    location = geoloc.geocode(address)
    match = re.search(expr, location.address)
    if match:   
        return match.group(0)
    else:
        return None
    

def populate_postal_codes(
        geoloc: Nominatim,
        addresses: pd.DataFrame, 
        sleep_time: int = SLEEP_TIME, 
        max_addresses: Optional[int] = MAX_ADDRESSES
    ) -> pd.DataFrame:
    """
    Populate the postal codes for the addresses.

    Args:
        geoloc: Geolocator object
        addresses: DataFrame containing the addresses
        sleep_time: Time to sleep between requests to the nominatim server
        max_addresses: Maximum number of addresses to process
    """
    # Create a copy of the addresses DataFrame to avoid the SettingWithCopyWarning
    addresses = addresses.copy()
    
    # Initialize the POSTAL_CODE column with None values
    addresses['POSTAL_CODE'] = None
    
    # Output file path
    output_file = f'data/truncated_address_data_with_postal_codes_{START_INDEX}.csv'
    
    # NOTE: This is deliberately slow to not overload the 
    # nominatim server
    i = 0
    for idx, address in tqdm(addresses.iterrows(), total=min(max_addresses, len(addresses))):
        if idx < START_INDEX:
            continue
        if max_addresses and i >= max_addresses:
            break
        try:
            postal_code = get_postal_code(geoloc, address['ADDRESS_FULL'])
            addresses.loc[idx, 'POSTAL_CODE'] = postal_code
            # Write to CSV after each successful lookup
            addresses.to_csv(output_file, index=False)
            time.sleep(sleep_time)
            i += 1
        except Exception as e:
            print(f"Error getting postal code for {address['ADDRESS_FULL']}: {e}")
            # Still write to CSV even if there was an error, to preserve progress
            addresses.to_csv(output_file, index=False)
            continue

    return addresses


if __name__ == "__main__":
    main(
        data_path='data/address_data.csv',
        sleep_time=SLEEP_TIME,
        max_addresses=MAX_ADDRESSES
    )

