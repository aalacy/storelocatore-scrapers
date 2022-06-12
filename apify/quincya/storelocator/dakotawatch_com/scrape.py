import json

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://storemapper-herokuapp-com.global.ssl.fastly.net/api/users/15037/stores.js?callback=SMcallback2"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    locator_domain = "https://dakotawatch.com/"

    stores = json.loads(base.text.split('stores":')[1].split("})")[0])

    for store in stores:
        location_name = store["name"].replace("  ", " ")
        raw_address = store["address"].split(",")
        street_address = raw_address[0]
        city = raw_address[1]
        state = raw_address[2].replace("W.", "").strip()
        zip_code = raw_address[3]
        country_code = "US"
        store_number = store["id"]
        phone = store["phone"]
        location_type = ""
        latitude = store["latitude"]
        longitude = store["longitude"]
        hours_of_operation = ""

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url="https://dakotawatch.com/location-finder/",
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
