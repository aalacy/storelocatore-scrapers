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

    base_link = "https://www.wincofoods.com/stores/?coordinates=34.264406683768875,-93.34875642499999&zoom=4"
    user_agent = (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
    )

    driver = SgChrome(user_agent=user_agent).driver()
    driver.get(base_link)
    time.sleep(15)

    base = BeautifulSoup(driver.page_source, "lxml")
    driver.close()

    items = base.find(class_="store-list__scroll-container").find_all("li")
    locator_domain = "https://www.wincofoods.com/"

    for item in items:
        location_name = " ".join(list(item.find(class_="name").stripped_strings)[:2])
        street_address = list(item.find(class_="address1").stripped_strings)[-1]
        city = list(item.find(class_="city").stripped_strings)[-1]
        state = list(item.find(class_="state").stripped_strings)[-1]
        zip_code = list(item.find(class_="zip").stripped_strings)[-1]
        country_code = "US"
        location_type = ""
        store_number = item["id"].split("-")[-1]
        hours_of_operation = list(
            item.find(class_="store-preview__status").stripped_strings
        )[-1].title()

        link = "https://www.wincofoods.com/stores/" + store_number

        phone = "<INACCESSIBLE>"
        latitude = "<INACCESSIBLE>"
        longitude = "<INACCESSIBLE>"
        hours_of_operation = "<INACCESSIBLE>"

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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
