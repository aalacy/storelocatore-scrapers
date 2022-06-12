import json

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.boathouserestaurants.ca/store-locator/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    js = str(base).split("locations:")[1].split("}}],")[0] + "}}]"
    stores = json.loads(js)

    for store in stores:
        locator_domain = "boathouserestaurants.ca"
        location_name = store["name"]
        street_address = store["street"]
        city = store["city"]
        state = store["state"]
        zip_code = store["postal_code"]
        country_code = "CA"
        store_number = store["id"]
        location_type = "<MISSING>"
        phone = store["phone_number"]
        latitude = store["lat"]
        longitude = store["lng"]
        hours_of_operation = BeautifulSoup(store["hours"], "lxml").p.get_text(" ")
        link = "https://www.boathouserestaurants.ca" + store["url"]

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
