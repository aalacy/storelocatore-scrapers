import time

from bs4 import BeautifulSoup as bs
from sgscrape.sgpostal import parse_address_intl
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


DOMAIN = "cwclogon.com"
website = "https://www.cwclogon.com/"
MISSING = "<MISSING>"


log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)


def get_driver(url, class_name, driver=None):
    if driver is not None:
        driver.quit()

    user_agent = (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
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


def getAddress(raw_address):
    try:
        if raw_address is not None and raw_address != MISSING:
            data = parse_address_intl(raw_address)
            street_address = data.street_address_1
            if data.street_address_2 is not None:
                street_address = street_address + " " + data.street_address_2
            city = data.city
            state = data.state
            zip_postal = data.postcode

            if street_address is None or len(street_address) == 0:
                street_address = MISSING
            if city is None or len(city) == 0:
                city = MISSING
            if state is None or len(state) == 0:
                state = MISSING
            if zip_postal is None or len(zip_postal) == 0:
                zip_postal = MISSING
            return street_address, city, state, zip_postal
    except Exception as e:
        log.info(f"No valid address {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def getLatLongFromMapUrl(page_url):
    if "/@" not in page_url:
        return MISSING, MISSING
    part = page_url.split("/@")[1]
    if "/" not in part:
        return MISSING, MISSING
    part = part.split("/")[0]
    if "," not in part:
        return MISSING, MISSING
    parts = part.split(",")
    return parts[0], parts[1]


def fetchData():
    x = 0
    while True:
        x = x + 1
        class_name = "fusion-row"
        url = f"{website}locations"
        if x == 1:
            driver = get_driver(url, class_name)
        else:
            driver = get_driver(url, class_name, driver=driver)
        soup = bs(driver.page_source, "html.parser")
        grid1 = soup.find_all("div", class_="fusion-builder-row fusion-row")[2]
        grids = grid1.find_all("div", class_="fusion-layout-column")
        if len(grids) == 0:
            continue
        else:
            break
        driver.quit()

    for grid in grids:
        address = grid.find("div", class_="fusion-text")
        page = grid.find("div", class_="fusion-aligncenter")
        if address is not None:
            raw_address = address.find("p").text
            street_address, city, state, zip_postal = getAddress(raw_address)
            page_url = page.find("a")["href"]
            driver = get_driver(page_url, class_name)
            time.sleep(15)
            soup = bs(driver.page_source, "html.parser")
            location_name = soup.find("h1", class_="entry-title").text
            location_name = location_name.replace("Location:", "").strip()
            log.info(f"Now grabbing data from: {page_url}")
            links = soup.find_all("a", attrs={"target": "_blank"})
            driver.quit()
            for link in links:
                gmap = link.get("href")
                if "https://www.google.com/maps/dir" in gmap:
                    latitude, longitude = getLatLongFromMapUrl(gmap)

            store_number = MISSING
            location_type = "Commercial Warehouse"
            country_code = "US"
            phone = MISSING
            hours_of_operation = MISSING

            yield SgRecord(
                locator_domain=DOMAIN,
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
    log.info("Crawling started ...")
    start = time.time()
    result = fetchData()
    count = 0
    with SgWriter() as writer:
        for rec in result:
            writer.write_row(rec)
            count = count + 1
    end = time.time()
    log.info(f"Finished grabbing and added {count} rows.")
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
