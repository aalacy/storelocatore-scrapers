from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from sgscrape.sgpostal import parse_address_intl
import time
import json


def fetch_data():
    locator_domain = "https://www.chocolatsfavoris.com/"
    base_url = "https://www.chocolatsfavoris.com/stores"
    json_url = (
        "https://maps.googleapis.com/maps/api/place/js/PlaceService.GetPlaceDetails"
    )
    with SgChrome() as driver:
        driver.get(base_url)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    '//div[@class="store-map"]',
                )
            )
        )
        locations = driver.find_elements_by_xpath(
            '//div[@class="store-map"]//div[@role="button"]'
        )
        for loc in locations:
            driver.execute_script("arguments[0].click();", loc)
            time.sleep(1)

        for rr in driver.requests:
            if rr.url.startswith(json_url) and rr.response:
                _ = json.loads(
                    " ".join(
                        rr.response.body.decode("utf-8")
                        .replace("\n", "")
                        .split("(")[1:]
                    )
                    .strip()[:-1]
                    .strip()
                )
                addr = parse_address_intl(_["result"]["formatted_address"])
                hours = []
                if "opening_hours" in _["result"]:
                    hours = _["result"]["opening_hours"]["weekday_text"]
                yield SgRecord(
                    page_url=base_url,
                    location_name=_["result"]["name"],
                    street_address=addr.street_address_1,
                    city=addr.city,
                    state=addr.state,
                    latitude=_["result"]["geometry"]["location"]["lat"],
                    longitude=_["result"]["geometry"]["location"]["lng"],
                    zip_postal=addr.postcode,
                    country_code=addr.country,
                    phone=_["result"]["formatted_phone_number"],
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours).replace("–", "-"),
                )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
