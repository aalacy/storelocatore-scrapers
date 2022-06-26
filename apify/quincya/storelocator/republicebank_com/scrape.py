import ssl
import time
from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

import undetected_chromedriver as uc
from webdriver_manager.chrome import ChromeDriverManager

ssl._create_default_https_context = ssl._create_unverified_context


def fetch_data(sgw: SgWriter):

    raw_link = "https://republicebank.locatorsearch.com/GetItems.aspx"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    locator_domain = "republicebank.com"

    payload = {
        "lat": "42.011295",
        "lng": "-87.73964",
        "searchby": "FCS|",
        "SearchKey": "",
        "rnd": "1656034914901",
    }
    req = session.post(raw_link, data=payload, headers=headers)
    base = BeautifulSoup(req.text, "lxml")
    raw_items = base.markers.find_all("marker")

    base_link = "https://republicebank.locatorsearch.com/index.aspx?s=FCS#"
    options = uc.ChromeOptions()
    options.headless = True

    with uc.Chrome(
        driver_executable_path=ChromeDriverManager().install(), options=options
    ) as driver:
        driver.get(base_link)
        time.sleep(5)
        base = BeautifulSoup(driver.page_source, "lxml")

        items = base.table.find_all(class_="row")
        for i, item in enumerate(items):
            raw_data = list(item.span.stripped_strings)
            location_name = item.b.text.strip()
            street_address = raw_data[0]
            if "1st Floor" in location_name:
                street_address = street_address + " 1st Floor"
                location_name = location_name.replace("1st Floor", "").strip()
            city_line = raw_data[1].strip().split(",")
            city = city_line[0].strip()
            state = city_line[-1].strip().split()[0].strip()
            zip_code = city_line[-1].strip().split()[1].strip()
            country_code = "US"
            store_number = item["id"].replace("tablerow", "")
            phone = raw_data[2]
            location_type = ""
            latitude = raw_items[i]["lat"]
            longitude = raw_items[i]["lng"]
            hours_of_operation = raw_items[i].table.get_text(" ")

            sgw.write_row(
                SgRecord(
                    locator_domain=locator_domain,
                    page_url="https://republicebank.com/locations/",
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
