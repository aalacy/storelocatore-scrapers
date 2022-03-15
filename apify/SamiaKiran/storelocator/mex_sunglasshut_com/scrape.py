import time
import unicodedata
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgselenium.sgselenium import SgChrome
from selenium.webdriver.common.keys import Keys
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgpostal.sgpostal import parse_address_intl
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context


session = SgRequests()
website = "mex_sunglasshut_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://mex.sunglasshut.com"
MISSING = SgRecord.MISSING


state_list = [
    "Aguascalientes",
    "Baja California",
    "Baja California Sur",
    "Campeche",
    "Chiapas",
    "Chihuahua",
    "Coahuila",
    "Colima",
    "Durango",
    "Federal District",
    "Guanajuato",
    "Guerrero",
    "Hidalgo",
    "Jalisco",
    "México",
    "Michoacán",
    "Morelos",
    "Nayarit",
    "Nuevo León",
    "Oaxaca",
    "Puebla",
    "Querétaro",
    "Quintana Roo",
    "San Luis Potosí",
    "Sinaloa",
    "Sonora",
    "Tabasco",
    "Tamaulipas",
    "Tlaxcala",
    "Veracruz",
    "Yucatán",
    "Zacatecas",
]


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    if True:
        for temp_state in state_list:
            with SgChrome() as driver:
                url = "https://mex.sunglasshut.com/Encuentra-tu-tienda"
                driver.get(url)
                try:
                    state_name = driver.find_element_by_xpath(
                        "//input[contains(@class, 'pac-target-input')]"
                    )
                except:
                    continue
                state_name.send_keys(temp_state)
                log.info(f"Fetching locations from {temp_state}")
                state_name.send_keys(Keys.ENTER)
                time.sleep(15)
                soup = BeautifulSoup(driver.page_source, "html.parser")
                loclist = soup.findAll(
                    "li", {"class": "sunglasshutmx-store-locator-0-x-listMarker"}
                )
                if not loclist:
                    continue
                for loc in loclist:
                    location_name = (
                        loc.find(
                            "span",
                            {
                                "class": "sunglasshutmx-store-locator-0-x-addressStoreName"
                            },
                        )
                        .get_text(separator="|", strip=True)
                        .replace("|", "")
                    )
                    location_name = strip_accents(location_name)
                    log.info(location_name)
                    try:
                        phone = loc.select_one("a[href*=tel]").text
                    except:
                        phone = MISSING
                    raw_address = (
                        loc.find(
                            "span",
                            {
                                "class": "sunglasshutmx-store-locator-0-x-addressStoreAddress"
                            },
                        )
                        .get_text(separator="|", strip=True)
                        .replace("|", " ")
                    )
                    raw_address = raw_address.split("Instrucciones")[0]
                    pa = parse_address_intl(raw_address)

                    street_address = pa.street_address_1
                    street_address = street_address if street_address else MISSING

                    city = pa.city
                    city = city.strip() if city else MISSING

                    state = pa.state
                    state = state.strip() if state else MISSING

                    zip_postal = pa.postcode
                    zip_postal = zip_postal.strip() if zip_postal else MISSING

                    hours_of_operation = "<INACCESSIBLE>"
                    country_code = "MX"
                    yield SgRecord(
                        locator_domain=DOMAIN,
                        page_url=url,
                        location_name=location_name,
                        street_address=street_address.strip(),
                        city=city.strip(),
                        state=state.strip(),
                        zip_postal=zip_postal.strip(),
                        country_code=country_code,
                        store_number=MISSING,
                        phone=phone.strip(),
                        location_type=MISSING,
                        latitude=MISSING,
                        longitude=MISSING,
                        hours_of_operation=hours_of_operation,
                        raw_address=raw_address,
                    )


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
