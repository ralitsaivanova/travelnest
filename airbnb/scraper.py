from playwright.sync_api import sync_playwright, Playwright
from pprint import pprint
import re
import time
from typing import List

import parsing


def run(playwright: Playwright, resource_ids: List[int]) -> List[parsing.AbnbResult]:
    # for simplicity I am using the same browser
    # and ignoring any possible fingerprinting or botnet concerns
    chromium = playwright.chromium
    browser = chromium.launch()
    page = browser.new_page()
    url = "https://www.airbnb.co.uk/rooms/"

    results = []
    for resource_id in resource_ids:
        response = page.goto(f"{url}/{resource_id}")

        if response.status == "410":
            # resource not available
            continue

        print(f"scraping resource id {resource_id}")
        # giving it time to load
        print("sleeping for 2 secs")
        time.sleep(2)

        parsed_scraped_data = {}

        overview_info = page.query_selector_all('//div[@data-section-id="OVERVIEW_DEFAULT_V2"]')
        if not overview_info:
            # not interested in amenities if no overview info found
            print(f"scraping resource id {resource_id} not found")
            continue

        for item in overview_info:
            overview_line = item.query_selector("ol").text_content()
            parsed_scraped_data = parsing.parse_overview_line(
                resource_id=resource_id, line=overview_line
            )

        # using the same page and browser for the second request as well
        # to get closer to simulating a human interraction
        # "amenities" is forbidden in the robots.txt file
        page.get_by_role("button", name=re.compile("amenities", re.IGNORECASE)).click()

        # giving it time to load
        print("sleeping for 1 secs")
        time.sleep(1)

        parsed_scraped_data["amenities"] = parsing.parse_amenities_list(
            page_content=page.content()
        )

        try:
            results.append(parsing.AbnbResult(resource_id, **parsed_scraped_data))
        except TypeError as type_err:
            # this can be an opportunity to understand what part or the result
            # we expect is not working accordingly which means the scraper
            # may need attention and recalibrating
            pass

    browser.close()

    return results


with sync_playwright() as abnb_scraper:
    ids = [33571268, 20669368, 50633275]

    result = run(abnb_scraper, resource_ids=ids)
    pprint(result)
