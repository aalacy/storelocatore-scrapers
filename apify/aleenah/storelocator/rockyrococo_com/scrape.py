import time
from sglogging import sglog
from bs4 import BeautifulSoup
from sgselenium import SgChrome
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

session = SgRequests()
website = "rockyrococo_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()


headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}


DOMAIN = "https://rockyrococo.com"
MISSING = SgRecord.MISSING


def fetch_data():
    states = ["MN", "WI"]
    with SgChrome(executable_path="C:/webdrivers/chromedriver.exe") as driver:
        url = "https://rockyrococo.com/locations"
        driver.get(url)
        time.sleep(10)
        driver.switch_to.frame(driver.find_element_by_id("bullseye_iframe"))
        for us in states:
            log.info(f"Fetching locations from {us}...")
            driver.find_element_by_id("txtCityStateZip").clear()
            driver.find_element_by_id("txtCityStateZip").send_keys(us)
            driver.find_element_by_id("ContentPlaceHolder1_searchButton").click()
            time.sleep(10)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            loclist = soup.findAll("div", {"class": "itemWrap"})
            for loc in loclist:
                temp = loc.find("a", {"id": "website"})["href"]
                location_name = loc.find("h3", {"itemprop": "name"}).text
                coords = loc.find("div", {"itemprop": "geo"})
                latitude = coords.find("meta", {"itemprop": "latitude"})["content"]
                longitude = coords.find("meta", {"itemprop": "longitude"})["content"]
                street_address = loc.find("span", {"itemprop": "streetAddress"}).text
                log.info(street_address)
                city = loc.find("span", {"itemprop": "addressLocality"}).text
                state = loc.find("span", {"itemprop": "addressRegion"}).text
                zip_postal = loc.find("span", {"itemprop": "postalCode"}).text
                phone = loc.find("span", {"itemprop": "telephone"}).text
                if "http" in temp:
                    page_url = temp
                elif "https:" not in temp:
                    page_url = "http:" + temp
                page_url = page_url.replace("/http:/", "http:/")
                if "rockysmadison" in temp:
                    page_url = url
                    hours_of_operation = MISSING
                else:
                    r = session.get(page_url, headers=headers)
                    soup = BeautifulSoup(r.text, "html.parser")
                    hours_of_operation = r.text.split("Hours:")[1]
                    if "View" in hours_of_operation:
                        hours_of_operation = hours_of_operation.split("View")[0]
                    elif "Apply" in hours_of_operation:
                        hours_of_operation = hours_of_operation.split("Apply")[0]
                    elif "Click" in hours_of_operation:
                        hours_of_operation = hours_of_operation.split("Click")[0]

                    hours_of_operation = BeautifulSoup(
                        hours_of_operation, "html.parser"
                    )
                    hours_of_operation = (
                        hours_of_operation.get_text(separator="|", strip=True)
                        .replace("|", " ")
                        .replace("Menu", "")
                        .replace("Apply Now", "")
                        .replace("Click here for local information!", "")
                    )
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
