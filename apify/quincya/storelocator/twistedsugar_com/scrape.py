import ssl
import time

from bs4 import BeautifulSoup

from sglogging import sglog

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgselenium.sgselenium import SgChrome

log = sglog.SgLogSetup().get_logger("twistedsugar.com")

ssl._create_default_https_context = ssl._create_unverified_context


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"

    base_link = "https://twistedsugar.com/twisted-sugar-stores/all"

    locator_domain = "https://twistedsugar.com"

    driver = SgChrome(user_agent=user_agent).driver()

    driver.get(base_link)
    base = BeautifulSoup(driver.page_source, "lxml")

    states = base.find_all(class_="col-sm-6")

    for i in states:
        link = locator_domain + i.a["href"]
        log.info(link)
        driver.get(link)
        time.sleep(2)
        WebDriverWait(driver, 50).until(
            ec.presence_of_element_located((By.CLASS_NAME, "tableHeading"))
        )
        time.sleep(2)
        base = BeautifulSoup(driver.page_source, "lxml")

        items = base.find_all(class_="col-sm-6")
        for item in items:
            location_name = item.find(class_="tableHeadingText").text.strip()
            street_address = (
                item.find(class_="menuTextHeading").text.split(", Provo")[0].strip()
            ).replace("street.", "street")
            try:
                city_line = (
                    item.find_all(class_="menuTextHeading")[1].text.strip().split(",")
                )
            except:
                continue
            city = city_line[0].strip()
            state = " ".join(city_line[-1].strip().split()[:-1]).strip()
            zip_code = city_line[-1].strip().split()[-1].strip()
            if not zip_code.isdigit():
                zip_code = ""
            if city == "Provo":
                state = "Utah"
            country_code = "US"
            store_number = ""
            phone = item.find(class_="displayHeadingText").text.strip()
            location_type = "Location"
            if "Food Truck" in street_address:
                location_type = "Food Truck"
            if ")" in street_address:
                street_address = street_address.split(")")[1].strip()
            latitude = ""
            longitude = ""
            hours_of_operation = " ".join(list(item.table.stripped_strings))

            sgw.write_row(
                SgRecord(
                    locator_domain=locator_domain,
                    page_url=link,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip_code,
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone,
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                )
            )

    driver.close()


with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))) as writer:
    fetch_data(writer)
