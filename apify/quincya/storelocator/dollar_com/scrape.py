from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgselenium.sgselenium import SgChrome
import json
import time
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

locator_domain = "dollar.com"
base_link = "https://www.dollar.com/loc/modules/multilocation/?near_location=US&services__in=&published=1&within_business=true&limit=2000"

user_agent = (
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
)


def fetch_data(sgw: SgWriter):

    with SgChrome(user_agent=user_agent) as driver:

        driver.get(base_link)
        time.sleep(30)
        stores = json.loads(driver.find_element_by_css_selector("body").text)["objects"]
        driver.close()
        found = []
        for store in stores:
            location_name = store["location_name"]
            try:
                street_address = (store["street"] + " " + store["street2"]).strip()
            except:
                street_address = store["street"].strip()

            if " CLOSE " in street_address.upper():
                continue

            if street_address in found:
                continue
            found.append(street_address)

            city = store["city"]
            state = store["state"]
            if not state:
                state = "<MISSING>"
            zip_code = store["postal_code"]
            country_code = store["country"]
            store_number = store["id"]
            location_type = "<MISSING>"
            try:
                phone = store["phonemap"]["phone"]
            except:
                phone = "<MISSING>"
            hours_of_operation = ""
            raw_hours = store["formatted_hours"]["primary"]["days"]
            for hour in raw_hours:
                hours_of_operation = (
                    hours_of_operation + " " + hour["label"] + " " + hour["content"]
                ).strip()
            latitude = store["lat"]
            longitude = store["lon"]
            link = store["location_url"]

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
