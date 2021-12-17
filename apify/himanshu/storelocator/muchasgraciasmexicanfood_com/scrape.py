import re
import time
from bs4 import BeautifulSoup
from sgselenium import SgChrome
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

log = sglog.SgLogSetup().get_logger(logger_name="muchasgraciasmexicanfood.com")


def fetch_data():

    base_url = "https://www.muchasgraciasmexicanfood.com/locations/"

    with SgChrome() as driver:

        driver.get(base_url)
        time.sleep(8)

        base = BeautifulSoup(driver.page_source, "lxml")

        items = base.find_all(class_="sl-item")

        for i, location_soup in enumerate(items):
            location_name = location_soup.find(class_="p-title").text.strip()
            addr = list(location_soup.find(class_="p-area").stripped_strings)
            street_address = addr[0].strip()
            city_line = addr[1].split(",")
            city = city_line[0].strip()
            state = city_line[1].strip()
            zipp = city_line[2].strip()

            try:
                phone = re.findall(r"\([\d]{3}\) [\d]{3}-[\d]{4}", location_soup.text)[
                    0
                ]
            except:
                phone = "<MISSING>"

            days = ""
            hours = ""
            ps = location_soup.find_all(class_="p-area")
            for p in ps:
                if "mon," in p.text.lower():
                    days = p.text
                if ":00 " in p.text.lower():
                    hours = p.text.strip()

            if days and hours:
                hours_of_operation = hours + days
            else:
                hours_of_operation = "<MISSING>"

            if "24 Hours" in location_soup.text:
                hours_of_operation = "Open 24 Hours"

            driver.find_elements_by_class_name("sl-item")[i].click()
            time.sleep(2)
            try:
                raw_gps = driver.find_element_by_xpath(
                    "//a[contains(@title,'Open this area in Google Maps (opens a new window)')]"
                ).get_attribute("href")
                latitude = raw_gps[raw_gps.find("=") + 1 : raw_gps.find(",")].strip()
                longitude = raw_gps[raw_gps.find(",") + 1 : raw_gps.find("&")].strip()

            except:
                raise
                latitude = "<MISSING>"
                longitude = "<MISSING>"

            yield SgRecord(
                locator_domain="muchasgraciasmexicanfood.com",
                page_url=base_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zipp,
                country_code="US",
                store_number="<MISSING>",
                phone=phone,
                location_type="<MISSING>",
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {
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

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
