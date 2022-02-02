import time
from bs4 import BeautifulSoup as bs
import re

from sgpostal.sgpostal import parse_address_intl
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

from sgselenium.sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

import ssl

ssl._create_default_https_context = ssl._create_unverified_context


DOMAIN = "pizzadepot.ca"
MISSING = "<MISSING>"

website = "https://www.pizzadepot.ca"
locations_page = "https://www.pizzadepot.ca/location/"

log = sglog.SgLogSetup().get_logger(logger_name=website)

session = SgRequests()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
}


def get_driver(url, xpath_name, driver=None):
    if driver is not None:
        driver.quit()

    user_agent = (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
    )
    x = 0
    while True:
        x = x + 1
        try:
            log.info(f"Retrying: {x}")
            driver = SgChrome(
                executable_path=ChromeDriverManager().install(),
                user_agent=user_agent,
                is_headless=True,
            ).driver()
            driver.get(url)
            driver.switch_to.frame(0)
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, xpath_name))
            )
            html = driver.page_source
            mapembedaddress = bs(html, "html.parser")
            address = mapembedaddress.find("div", {"class": "address"}).text
            driver.switch_to.default_content()
            break
        except Exception as e:
            driver.quit()
            if x == 3:
                log.info(f"Page is not valid {url} : {e}")
                break
            return driver, MISSING
            continue

    return driver, address


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


def parseCentrod(url):
    lon = re.findall(r"2d{1}(-?\d*.{1}\d*)!{1}", url)[0]
    lat = re.findall(r"3d{1}(-?\d*.{1}\d*)!{1}", url)[0]
    return lat, lon


def fetchData():
    xpath_name = '//div[@class="address"]'
    response = session.get(locations_page, headers=headers)
    soup = bs(response.text, "html.parser")
    grids = soup.find_all(
        "a", {"class": "elementor-button-link elementor-button elementor-size-md"}
    )

    for grid in grids:
        page_url = website + grid.get("href")
        log.info(f"Now Crawling: {page_url}")
        driver, raw_address = get_driver(page_url, xpath_name)
        if raw_address == MISSING:
            continue
        time.sleep(15)
        street_address, city, state, zip_postal = getAddress(raw_address)
        html = driver.page_source
        soup2 = bs(html, "html.parser")
        try:
            location_name = soup2.find_all(
                "h3", class_="elementor-heading-title elementor-size-default"
            )[1].text
            log.info(f"Location Name: {location_name}")
        except:
            location_name = soup2.find_all(
                "h2", class_="elementor-heading-title elementor-size-default"
            )[1].text
            if "Hours" in str(location_name):
                location_name = soup2.find_all(
                    "h2", class_="elementor-heading-title elementor-size-default"
                )[0].text
            log.info(f"Location Name: {location_name}")

        location_type = MISSING
        if "Coming Soon" in str(location_name):
            location_type = "Coming Soon"
        elif "Temporarily closed" in str(location_name):
            location_type = "Temporarily closed"
        elif "Opening Soon" in str(location_name):
            location_type = "Coming Soon"

        iframe = soup2.find("iframe", attrs={"loading": "lazy"})
        latlonUrl = iframe["src"]
        latitude, longitude = parseCentrod(latlonUrl)
        log.info(f"LatLon: {latitude}, {longitude}")
        phone = soup2.find_all("span", class_="elementor-icon-list-text")[2].text
        if phone == "Chicken Menu":
            phone = soup2.find_all("span", class_="elementor-icon-list-text")[1].text
        _tmp = []
        try:
            hoosearch = soup2.findAll(text="Hours")[0].findNext("p")
            if "Sunday" in str(hoosearch):
                hoo = str(hoosearch).split("<br/>")
                for h in hoo[0:4]:
                    hr = (
                        h.replace("\n", "")
                        .replace("\n\r", "")
                        .replace("<p>", "")
                        .replace("</p>", "")
                        .strip()
                    )
                    _tmp.append(hr)
                hours_of_operation = hours_of_operation = "; ".join(_tmp) or MISSING
        except:
            hours_of_operation = MISSING

        driver.quit()

        yield SgRecord(
            locator_domain=DOMAIN,
            store_number="",
            page_url=page_url,
            location_name=location_name.strip(),
            location_type=location_type,
            street_address=street_address,
            city=city,
            zip_postal=zip_postal,
            state=state,
            country_code="CA",
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
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in result:
            writer.write_row(rec)
            count = count + 1
    end = time.time()
    log.info(f"Finished grabbing and added {count} rows.")
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
