import json

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://qualitymartnc.com/locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    locator_domain = "qualitymartnc.com"

    js = str(base).split('places":')[1].split("]}]")[0] + "]}]"
    store_data = json.loads(js)

    for store in store_data:
        location_name = store["title"].upper()
        street_address = store["address"].split(", Durham")[0]
        city = store["location"]["city"]
        state = store["location"]["state"]
        zip_code = store["location"]["postal_code"]
        country_code = "US"
        store_number = location_name.split("#")[1]

        location_type = ""
        raw_types = store["categories"]
        for row in raw_types:
            location_type = (location_type + ", " + row["name"]).strip()
        location_type = location_type[1:].strip()

        phone = store["location"]["extra_fields"]["phone-number"]
        hours_of_operation = store["location"]["extra_fields"]["hours"]
        latitude = store["location"]["lat"]
        longitude = store["location"]["lng"]

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
