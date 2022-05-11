import ssl
import time

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgselenium.sgselenium import SgChrome

ssl._create_default_https_context = ssl._create_unverified_context


def fetch_data(sgw: SgWriter):

    base_link = "https://www.toysrus.com.bn/stores/"

    user_agent = (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
    )

    driver = SgChrome(user_agent=user_agent).driver()
    driver.get(base_link)
    time.sleep(10)
    driver.find_element_by_css_selector(".store-item").click()
    time.sleep(2)
    base = BeautifulSoup(driver.page_source, "lxml")
    driver.close()

    locator_domain = "https://www.toysrus.com.bn"

    stores = base.find_all(class_="result")
    for store in stores:
        location_name = store.find(class_="name").text.strip()
        raw_address = list(store.find(class_="main").stripped_strings)
        street_address = raw_address[0].split(",")[0] + " " + raw_address[1]
        city = raw_address[0].split(",")[1].strip()
        state = ""
        zip_code = raw_address[2].split(",")[1].strip()
        country_code = "Brunei"
        store_number = store.find(class_="row store-heading")["data-store-id"]
        phone = store.find(class_="number").text.strip().replace("phone number", "")
        location_type = ""
        hours_of_operation = " ".join(
            list(store.find(class_="store-hours").stripped_strings)[3:]
        )
        latitude = base.find(class_="map-canvas")["data-initlat"]
        longitude = base.find(class_="map-canvas")["data-initlng"]

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url=base_link,
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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
