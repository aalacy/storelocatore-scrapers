from sglogging import SgLogSetup
from sgselenium import SgChrome
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
import time
from lxml import html
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


DOMAIN = "https://www.marriott.com"
URL_LOCATION = "https://www.marriott.com/hotel-search.mi"
MISSING = "<MISSING>"

logger = SgLogSetup().get_logger("marriott_com")

headers = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}


def fetch_data():

    items = []
    with SgChrome() as driver:
        addresses = []
        brand_id = "FP"
        driver.get(URL_LOCATION)
        data1 = html.fromstring(driver.page_source, "lxml")
        xpath_view_all_hotels = '//a[contains(text(), "View all hotels")]/@href'
        urls_countries = data1.xpath(xpath_view_all_hotels)
        urls_countries = [f"{DOMAIN}{url}" for url in urls_countries]
        logger.info(f" URLs for all countries: {urls_countries}")

        for rnum, region in enumerate(urls_countries):
            logger.info(f"URL  to be pulled: {region}")
            driver.get(region)
            xpath_webdrivewait = '//span[contains(text(), "Map View")]'
            WebDriverWait(driver, 40).until(
                EC.element_to_be_clickable((By.XPATH, xpath_webdrivewait))
            )
            time.sleep(30)

            while True:
                soup = BeautifulSoup(driver.page_source, "lxml")
                data = html.fromstring(driver.page_source, "lxml")
                for location in soup.find(
                    "div", {"class": "js-property-list-container"}
                ).find_all("div", {"data-brand": True}, recursive=False):
                    locator_domain = DOMAIN
                    detail_id = (
                        location.find("span", {"class": "l-property-name"})
                        .parent.parent["href"]
                        .split("=")[-1]
                    )
                    slug = location["data-marsha"]
                    page_url = "https://www.marriott.com/hotels/travel/" + str(slug)
                    location_name = location.find(
                        "span", {"class": "l-property-name"}
                    ).text
                    address = location.find("div", {"data-address-line1": True})
                    street_address = address["data-address-line1"]
                    if location.find("div", {"data-address-line2": True}):
                        street_address = (
                            street_address + " " + address["data-address-line2"]
                        )
                    city = address["data-city"] or MISSING
                    state = address["data-state"] or MISSING
                    zip_postal = address["data-postal-code"] or MISSING
                    country_code = address["data-country-description"] or MISSING
                    logger.info(
                        f"Street Address: {street_address} | City:{city} | State: {state}| Zip: {zip_postal}| Country Code: {country_code}"
                    )
                    store_number = MISSING
                    phone = address["data-contact"] or MISSING
                    phone = phone.split(";")[0] if phone else MISSING
                    location_type = location["data-brand"] or MISSING
                    latitude = json.loads(location["data-property"])["lat"] or MISSING
                    longitude = (
                        json.loads(location["data-property"])["longitude"] or MISSING
                    )
                    logger.info(f"Latitude: {latitude} | Longitude: {longitude}")
                    hours_of_operation = MISSING
                    raw_address = address.text
                    raw_address = " ".join(raw_address.split())
                    raw_address = raw_address if raw_address else MISSING
                    logger.info(f"Raw Address: {raw_address}")
                    yield SgRecord(
                        locator_domain=locator_domain,
                        page_url=page_url,
                        location_name=location_name,
                        street_address=street_address,
                        city=city,
                        state=state,
                        zip_postal=zip_postal,
                        country_code=country_code,
                        store_number=store_number,
                        phone=phone,
                        location_type=location_type,
                        latitude=latitude,
                        longitude=longitude,
                        hours_of_operation=hours_of_operation,
                        raw_address=raw_address,
                    )

                if soup.find("a", {"title": "Next"}):
                    logger.info("Next Page Clicked")
                    driver.find_element_by_xpath("//a[@title='Next']").click()
                else:
                    break


def scrape():
    logger.info("Started")
    count = 0
    with SgWriter() as writer:
        results = fetch_data_au()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
