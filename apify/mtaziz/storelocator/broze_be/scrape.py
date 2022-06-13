from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from webdriver_manager.firefox import GeckoDriverManager
from sgselenium import SgFirefox
from sgpostal.sgpostal import parse_address_intl
import time
import json
from random import randint
from gzip import decompress
import ssl
from lxml import html


ssl._create_default_https_context = ssl._create_unverified_context


STORE_LOCATOR = "https://www.broze.be/web/BrozeWSite.nsf/Magasins?OpenForm"
google_placeservice_getplacedetails = (
    "maps.googleapis.com/maps/api/place/js/PlaceService.GetPlaceDetails"
)
logger = SgLogSetup().get_logger("broze_be")


def get_raw_address(_):
    result = _["result"]
    addr_address = result["adr_address"]
    sel = html.fromstring(addr_address, "lxml")
    extracted_add = sel.xpath("//text()")
    ea = [" ".join(i.split()).replace(",", "") for i in extracted_add]
    ea = [i for i in ea if i]
    raw_add = ""
    if ea:
        raw_add = ", ".join(ea)

    return raw_add


def fetch_records(sgw: SgWriter):

    with SgFirefox(executable_path=GeckoDriverManager().install()) as driver:
        driver.get(STORE_LOCATOR)
        driver.implicitly_wait(5)
        xpath_iframe = '//div[@id="carte"]/iframe[contains(@src, "google.com/maps")]'
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    xpath_iframe,
                )
            )
        )
        element_iframe = driver.find_element(By.XPATH, xpath_iframe)
        driver.switch_to.frame(element_iframe)
        logger.info("iframe Loaded OK!")

        xpath_map_button = '//div[contains(@aria-label,"Map") and contains(@tabindex, "0")]//div[@role="button"]'

        # Make sure the contents of the page loaded, allow the driver to load it.

        locations = driver.find_elements(By.XPATH, xpath_map_button)
        logger.info(f"Locations: {locations}")
        logger.info(f"[LocationsCount: {len(locations)}]")
        for locid, loc in enumerate(locations[0:]):
            driver.execute_script("arguments[0].click();", loc)
            logger.info(f"{locid} | {loc} Location Clicked with Success!")
            driver.implicitly_wait(1)
            time.sleep(randint(3, 7))

        for rr in driver.requests:
            logger.info(f"Response URL: {rr.url}")
            if google_placeservice_getplacedetails in rr.url:
                logger.info(f"GetPlaceDetails URL Found: {rr.url}")
                response_body = rr.response.body
                decomp_data = decompress(response_body).decode("utf-8")
                decomp_data_list = decomp_data.replace("\n", "").split("(")[1:]
                decomp_str = " ".join(decomp_data_list).strip()[:-1].strip()

                _ = json.loads(decomp_str)
                formatted_address = _["result"]["formatted_address"]
                addr = parse_address_intl(formatted_address)
                hours = []
                if "opening_hours" in _["result"]:
                    hours = _["result"]["opening_hours"]["weekday_text"]
                place_id = _["result"]["place_id"]

                raw_address = get_raw_address(_)
                street_address = addr.street_address_1

                if (
                    "Chau. Verte 93, 4470, Saint-Georges-sur-Meuse, Belgium"
                    in raw_address
                ):
                    street_address = "Chau. Verte 93"

                if "Chau. de Namur 55, /1, 1400, Nivelles, Belgium" in raw_address:
                    street_address = "Chau. de Namur 55/1"

                zip_postal = addr.postcode
                if (
                    "1, Route de la Basse Sambre, 6061, Montiginies sur sambre, Belgium"
                    in raw_address
                ):
                    zip_postal = "6061"

                item = SgRecord(
                    page_url=STORE_LOCATOR,
                    location_name=_["result"]["name"],
                    street_address=street_address,
                    city=addr.city,
                    state=addr.state,
                    store_number=place_id,
                    latitude=_["result"]["geometry"]["location"]["lat"],
                    longitude=_["result"]["geometry"]["location"]["lng"],
                    zip_postal=zip_postal,
                    country_code=addr.country,
                    phone=_["result"]["formatted_phone_number"],
                    locator_domain="broze.be",
                    hours_of_operation="; ".join(hours).replace("–", "-"),
                    raw_address=raw_address,
                )
                yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STORE_NUMBER,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.LATITUDE,
                }
            )
        )
    ) as writer:
        results = fetch_records(writer)
        for rec in results:
            writer.write_row(rec)
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
