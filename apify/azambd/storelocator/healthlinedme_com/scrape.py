from lxml import html
import time
import json

from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord

from sgselenium.sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context


website = "https://www.healthlinedme.com"
MISSING = "<MISSING>"


log = sglog.SgLogSetup().get_logger(logger_name=website)


def driverSleep(driver, time=5):
    try:
        WebDriverWait(driver, time).until(
            EC.presence_of_element_located((By.ID, MISSING))
        )
    except Exception:
        log.info("DO not need sleep time")
        pass


def getHoo(body, location_name):
    hoo = []
    divHolders = body.xpath(
        '//div[@class="view-location-list"]/div[contains(@class, "location-list-row")]'
    )
    for divHolder in divHolders:
        name = divHolder.xpath(".//h3[@class='location-name']/text()")[0].strip()
        if name == location_name:
            lis = divHolder.xpath(
                ".//div[contains(@class, 'location-all-hours-table')]/ul/li"
            )
            for li in lis:
                spans = li.xpath(".//span/text()") + li.xpath(".//span/strong/text()")
                if len(spans) > 0:
                    hoo.append(" ".join(spans))
            return "; ".join(hoo)


def getAddress(body, location_name):
    divHolders = body.xpath('//div[contains(@class, "location-details-window")]')
    for divHolder in divHolders:
        name = divHolder.xpath(".//h3[@class='location-name']/text()")[0].strip()
        if name == location_name:
            return divHolder.xpath(
                ".//ul[contains(@class, 'location-address')]/li/text()"
            )


def convertData(body, divHolder, locData):
    location_name = divHolder.xpath(".//h3[@class='location-name']/text()")[0].strip()
    store = {"location_name": location_name}
    fData = None
    for data in locData:
        if location_name in data["Name"]:
            fData = data
            break
    if fData is None:
        return None

    location_name = divHolder.xpath(".//h3[@class='location-name']/text()")[0].strip()
    store["phone"] = (
        divHolder.xpath(".//li[@class='location-phone-main']/text()")[0]
        .replace("Phone:", "")
        .strip()
    )

    address = getAddress(body, location_name)
    address1 = address[1].strip()

    store["street_address"] = address[0].strip()
    store["city"] = address1.split(", ")[0]
    store["state"] = address1.split(", ")[1].split(" ")[0]
    store["zip_postal"] = address1.split(", ")[1].split(" ")[1]
    store["raw_address"] = (", ").join(address)
    store["hoo"] = getHoo(body, location_name)

    store["latitude"] = data["Lat"]
    store["longitude"] = data["Lng"]
    store["store_number"] = data["id"]
    return store


def fetchStores():
    user_agent = (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
    )
    x = 0
    driver = None
    while True:
        x = x + 1
        try:
            driver = SgChrome(
                executable_path=ChromeDriverManager().install(),
                user_agent=user_agent,
                is_headless=True,
            ).driver()
            driver.get(f"{website}/locations")
            found = False
            delay = 2
            while delay < 240:
                driverSleep(driver)
                log.debug(
                    f"Waiting to load location-details-window, delay={delay * 2}s"
                )

                if "location-details-window" in driver.page_source:
                    found = True
                    break
                delay = delay + 2

            if found is False:
                raise Exception("Can't overcome CF")
            body = html.fromstring(driver.page_source, "lxml")
            divHolders = body.xpath(
                '//div[@class="view-location-list"]/div[contains(@class, "location-list-row")]'
            )
            log.debug(f"Total location div found = {len(divHolders)}")

            driver.get(f"{website}/modules/locations/library/gmap.php")
            found = False
            delay = 2
            locData = []
            while delay < 240:
                driverSleep(driver)
                log.debug(f"Waiting to load json, delay={delay * 2}s")

                if '"Lat"' in driver.page_source:
                    found = True
                    data = driver.find_element_by_xpath("//pre").text
                    locData = json.loads(data)
                    break
                delay = delay + 2

            if found is False:
                raise Exception("Can't overcome CF")
            stores = []
            for divHolder in divHolders:
                stores.append(convertData(body, divHolder, locData))
            return stores

        except Exception as e:
            log.error(f"Error loading : {e}")
            driver.quit()
            if x == 1:
                raise Exception(
                    "Make sure this ran with a Proxy, will fail without one"
                )
            continue
    return []


def fetchData():
    stores = fetchStores()
    log.info(f"Total stores = {len(stores)}")
    for store in stores:
        store_number = store["store_number"]
        page_url = f"{website}/locations"
        location_name = store["location_name"]
        location_type = MISSING
        street_address = store["street_address"]
        city = store["city"]
        zip_postal = store["zip_postal"]
        state = store["state"]
        country_code = "US"
        phone = store["phone"]
        latitude = store["latitude"]
        longitude = store["longitude"]
        hours_of_operation = store["hoo"]
        raw_address = store["raw_address"]

        yield SgRecord(
            locator_domain=website,
            store_number=store_number,
            page_url=page_url,
            location_name=location_name,
            location_type=location_type,
            street_address=street_address,
            city=city,
            zip_postal=zip_postal,
            state=state,
            country_code=country_code,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )
    return []


def scrape():
    log.info("Scrape started ...")
    start = time.time()
    result = fetchData()
    with SgWriter() as writer:
        for rec in result:
            writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
