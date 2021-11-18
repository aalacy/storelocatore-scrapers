from sgselenium import SgChrome
from bs4 import BeautifulSoup
import time
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

logger = SgLogSetup().get_logger("saintlukeshealthsystem_org")


def parse_addy(addy):
    arr = addy.split(",")
    if len(arr) == 4:
        arr = [arr[0], arr[2], arr[3]]
    street_address = arr[0].strip()
    city = arr[1].strip()
    state_zip = arr[2].strip().split(" ")
    state = state_zip[0]
    zip_code = state_zip[1]

    return street_address, city, state, zip_code


def fetch_data():
    locator_domain = "https://www.saintlukeskc.org/"

    with SgChrome() as driver:
        driver.get(locator_domain)
        driver.implicitly_wait(5)

        link = driver.find_element_by_xpath('//a[contains(text(),"Locations")]')
        html = (
            link.find_element_by_xpath("..")
            .find_element_by_css_selector("ul")
            .get_attribute("innerHTML")
        )

        soup = BeautifulSoup(html, "html.parser")

        cats = soup.find_all("a")

        cat_links = [[cat.text, locator_domain[:-1] + cat["href"]] for cat in cats]

        for cat_obj in cat_links:
            location_type = cat_obj[0]
            link = cat_obj[1]
            if "field_location_type_target_id=" not in link:
                continue
            driver.get(link)
            driver.implicitly_wait(5)

            while True:

                locs = driver.find_elements_by_css_selector("div.geolocation")
                for loc in locs:
                    lat = loc.get_attribute("data-lat")
                    longit = loc.get_attribute("data-lng")

                    location_name = loc.find_element_by_css_selector("h4").text
                    logger.info(location_name)
                    addy = loc.find_element_by_css_selector("p.address").text

                    street_address, city, state, zip_code = parse_addy(addy)

                    street_address = street_address.split("Ste ")[0]

                    has_phone_number = loc.find_elements_by_css_selector(
                        "a.tel__number"
                    )

                    if len(has_phone_number) > 0:
                        phone_number = has_phone_number[0].text
                    else:
                        phone_number = "<MISSING>"

                    country_code = "US"

                    button = loc.find_elements_by_css_selector(
                        "div.location-result__button-wrapper"
                    )
                    if len(button) > 0:
                        page_url = (
                            button[0]
                            .find_element_by_css_selector("a")
                            .get_attribute("href")
                        )
                    else:
                        page_url = "<MISSING>"

                    hours = "<MISSING>"
                    store_number = "<MISSING>"
                    street_address = (
                        street_address.split("Suite")[0]
                        .strip()
                        .split("Unit")[0]
                        .strip()
                        .replace(",", "")
                        .strip()
                    )

                    yield SgRecord(
                        locator_domain=locator_domain,
                        page_url=page_url,
                        location_name=location_name,
                        street_address=street_address,
                        city=city,
                        state=state,
                        zip_postal=zip_code,
                        country_code=country_code,
                        store_number=store_number,
                        phone=phone_number,
                        location_type=location_type,
                        latitude=lat,
                        longitude=longit,
                        hours_of_operation=hours,
                    )

                next_button = driver.find_elements_by_css_selector(
                    "li.pager__item.pager__item--next"
                )
                time.sleep(5)

                if len(next_button) == 0:
                    break

                butt = next_button[0].find_element_by_css_selector("a")
                driver.execute_script("arguments[0].click();", butt)
                time.sleep(2)

                driver.implicitly_wait(5)


def scrape():
    logger.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_TYPE,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.ZIP,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
