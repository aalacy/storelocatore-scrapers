import ssl
import json
from sglogging import sglog
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

            WebDriverWait(driver, 10).until(
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
        soup = BeautifulSoup(driver.page_source, "html.parser")
        loclist = driver.page_source.split('<script type="application/ld+json">')[1:]
        if len(loclist) == 0:
            continue
        else:
            break
    coords_list = driver.page_source.split('"lat":')[1:]
    for loc in loclist:
        loc = json.loads(loc.split("</script>")[0])
        location_name = loc["name"]
        address = loc["address"]
        phone = address["telephone"]
        street_address = address["streetAddress"]
        city = address["addressLocality"]
        state = address["addressRegion"]
        zip_postal = address["postalCode"]
        for coords in coords_list:
            if str(phone) in coords:
                coords = coords.split(',"googlePlaceId"')[0].split(",")
                latitude = coords[0]
                longitude = coords[1].replace('"lng":', "")
                break
        country_code = "US"
        page_url = DOMAIN + city.lower()
        log.info(page_url)
        hours_of_operation = loc["openingHours"]
        hours_of_operation = " ".join(hours_of_operation)
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
