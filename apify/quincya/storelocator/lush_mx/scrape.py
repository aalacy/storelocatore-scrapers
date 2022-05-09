import ssl
import time
from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgpostal.sgpostal import parse_address_intl

from sgselenium.sgselenium import SgChrome
from selenium.webdriver.common.by import By

ssl._create_default_https_context = ssl._create_unverified_context


def fetch_data(sgw: SgWriter):

    base_link = "https://www.google.com/maps/d/u/0/embed?mid=1CG7nHKHrBirfBP7ejT5IpG_l0ZH-QTiK&ll=24.481240432946997%2C-81.12307317500002&z=5"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"

    driver = SgChrome(user_agent=user_agent).driver()
    driver.get(base_link)

    time.sleep(2)
    driver.find_element(By.CLASS_NAME, "i4ewOd-pzNkMb-ornU0b-b0t70b-Bz112c").click()
    time.sleep(2)
    raw_data = str(BeautifulSoup(driver.page_source, "lxml"))
    locs = raw_data.split("_pageData")[1].split(",[[[")

    items = driver.find_elements(By.CLASS_NAME, "suEOdc")[2:-1]
    locator_domain = "https://www.lush.mx/"

    for i in items:

        i.click()
        time.sleep(2)
        base = BeautifulSoup(driver.page_source, "lxml")
        item = list(base.find(id="featurecardPanel").stripped_strings)

        location_name = item[0]
        raw_address = item[4]
        addr = parse_address_intl(raw_address)
        try:
            street_address = addr.street_address_1 + " " + addr.street_address_2
        except:
            street_address = addr.street_address_1
        city = addr.city
        state = addr.state
        zip_code = addr.postcode
        country_code = "MX"
        location_type = ""
        store_number = ""
        phone = item[5]
        hours_of_operation = ""
        latitude = ""
        longitude = ""
        for loc in locs:
            if loc[0].isdigit() and location_name in loc:
                latitude = loc.split(",")[0]
                longitude = loc.split(",")[1].split("]")[0]

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url="https://www.lush.mx/tiendas",
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
                raw_address=raw_address,
            )
        )
        driver.find_element(
            By.CSS_SELECTOR,
            ".U26fgb.mUbCce.p9Nwte.HzV7m-tJHJj-LgbsSe.qqvbed-a4fUwd-LgbsSe.M9Bg4d",
        ).click()
        time.sleep(2)
    driver.close()


with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))) as writer:
    fetch_data(writer)
