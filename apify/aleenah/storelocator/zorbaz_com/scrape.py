import ssl
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

ssl._create_default_https_context = ssl._create_unverified_context

website = "zorbaz_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

DOMAIN = "https://www.zorbaz.com/"
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

            WebDriverWait(driver, 30).until(
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
        class_name = "pm-location"
        url = "https://www.zorbaz.com/locationz"
        if x == 1:
            driver = get_driver(url, class_name)
        else:
            driver = get_driver(url, class_name, driver=driver)
        response = driver.page_source
        loclist = (
            response.split("window.POPMENU_APOLLO_STATE = ")[1]
            .split("[]}};")[0]
            .split("RestaurantLocation:")[1:]
        )
        if len(loclist) == 0:
            continue
        else:
            break
    for loc in loclist:
        try:
            phone = loc.split('"displayPhone":"')[1].split('"')[0]
        except:
            continue
        location_name = loc.split('"name":"')[1].split('"')[0]
        page_url = DOMAIN + loc.split('"slug":"')[-1].split('"')[0]
        store_number = loc.split('"id":')[1].split(",")[0]
        log.info(location_name)
        street_address = loc.split('"streetAddress":"')[1].split('"')[0]
        city = loc.split('"city":"')[1].split('"')[0]
        state = loc.split('"state":"')[1].split('"')[0]
        zip_postal = loc.split('"postalCode":"')[1].split('"')[0]
        country_code = loc.split('"country":"')[1].split('"')[0]
        latitude = loc.split('"lat":')[1].split('"')[0]
        longitude = loc.split('"lng":')[1].split('"')[0]
        hours_of_operation = (
            loc.split('"schemaHours":[')[1]
            .split("]")[0]
            .replace('","', " ")
            .replace('"', "")
        )
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=zip_postal.strip(),
            country_code=country_code,
            store_number=store_number,
            phone=phone,
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
