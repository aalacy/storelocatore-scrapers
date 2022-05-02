import ssl
import json
import usaddress
from sglogging import sglog
from bs4 import BeautifulSoup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgselenium.sgselenium import SgChrome
from selenium.webdriver.common.by import By
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC


try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

website = "moesitaliansandwiches_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

DOMAIN = "https://www.moesitaliansandwiches.com"
MISSING = SgRecord.MISSING


def get_driver(url, class_name, driver=None):
    if driver is not None:
        driver.quit()

    user_agent = (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0"
    )
    x = 0
    while True:
        x = x + 1
        try:
            driver = SgChrome(
                executable_path=ChromeDriverManager().install(),
                user_agent=user_agent,
                is_headless=True,
            ).driver()
            driver.get(url)

            WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.CLASS_NAME, class_name))
            )
            break
        except Exception:
            driver.quit()
            if x == 10:
                raise Exception(
                    "Make sure this ran with a Proxy, will fail without one"
                )
            continue
    return driver


def fetch_data():
    x = 0
    while True:
        x = x + 1
        class_name = "location"
        url = "https://www.moesitaliansandwiches.com/locations"
        if x == 1:
            driver = get_driver(url, class_name)
        else:
            driver = get_driver(url, class_name, driver=driver)
        loclist = driver.page_source.split("customLocationContent")[1:]
        if len(loclist) == 0:
            continue
        else:
            break
    coords_list = driver.page_source.split('"lat":')[1:]
    for loc in loclist:
        loc = (
            '{"customLocationContent'
            + loc.split(',"showLocationPhotoInLocationSearch')[0]
            + "}"
        )
        loc = json.loads(loc)
        page_url = (
            DOMAIN
            + BeautifulSoup(loc["customLocationContent"], "html.parser").find("a")[
                "href"
            ]
        )
        log.info(page_url)
        driver = get_driver(page_url, class_name)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        location_name = soup.find("h4").text
        temp = soup.findAll("p")
        phone = temp[1].text
        address = temp[0].get_text(separator="|", strip=True).replace("|", " ")
        address = address.replace(",", " ")
        address = usaddress.parse(address)
        i = 0
        street_address = ""
        city = ""
        state = ""
        zip_postal = ""
        while i < len(address):
            temp = address[i]
            if (
                temp[1].find("Address") != -1
                or temp[1].find("Street") != -1
                or temp[1].find("Recipient") != -1
                or temp[1].find("Occupancy") != -1
                or temp[1].find("BuildingName") != -1
                or temp[1].find("USPSBoxType") != -1
                or temp[1].find("USPSBoxID") != -1
            ):
                street_address = street_address + " " + temp[0]
            if temp[1].find("PlaceName") != -1:
                city = city + " " + temp[0]
            if temp[1].find("StateName") != -1:
                state = state + " " + temp[0]
            if temp[1].find("ZipCode") != -1:
                zip_postal = zip_postal + " " + temp[0]
            i += 1
        hours_of_operation = (
            soup.find("div", {"class": "hours"})
            .get_text(separator="|", strip=True)
            .replace("|", " ")
            .replace("NOW OFFERING CURBSIDE SERVICE & DELIVERY THROUGH DOOR DASH", "")
        )
        for coords in coords_list:
            if location_name in coords:
                coords = coords.split(',"googlePlaceId"')[0].split(",")
                latitude = coords[0]
                longitude = coords[1].replace('"lng":', "")
                break
        country_code = "US"
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=zip_postal.strip(),
            country_code=country_code,
            store_number=MISSING,
            phone=phone.strip(),
            location_type=MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
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
