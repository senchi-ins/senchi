### Running the scaper

1. Install the dependencies

If you do not have uv installed, install it with:

```bash
pip install uv
```

Then install the dependencies:

```bash
uv sync
```

2. Run the playwright install script

```bash
uv run playwright install
```

3. Update the start index

The scraper can start from a specific checkpoint. The checkpoint index is the index of the row in the data file that the scraper will start from. To update the index, edit `CHECKPOINT_INDEX` in the `main.py` file.

4. Run the scraper

```bash
# From the root of the repository
cd experiments/rates

# Then run the scraper
uv run main.py
```

5. [Optional] Configure the scraper

The scraper can be configured to run in headless mode, to take screenshots, and to run in verbose mode. To configure the scraper, edit the `main.py` file under the `if __name__ == "__main__"` block.

- `headless`: Whether to run the scraper in headless mode. This will run the scraper without a visible browser window.
- `verbose`: Whether to run the scraper in verbose mode. This will print updates to the console each step.
- `screenshots`: Whether to take screenshots of the scraper. This will save a screenshot of the page to the `ss` directory.

### Notes

- You may see `error: unable to click / find element` errors. This is because the scraper is trying to click on an element that is not present on the page. This occurs because all paths are always tried, and the scraper will not stop until it has tried all paths. Therefore, if a page isn't there, you will see this error. Simply ignore it.
- Not all address data has been added to the data set. More addresses can be found in `data/address_data/truncated_address_data_with_postal_codes.csv` or in `ins/address_data` on sharepont.