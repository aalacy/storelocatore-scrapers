import json

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.fountaintire.com/umbraco/api/locations/get"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    # Request post
    payload = {
        "latitude": "51.253775",
        "longitude": "-85.323214",
        "radius": "5000",
        "services": "",
    }

    req = session.post(base_link, headers=headers, data=payload)
    base = BeautifulSoup(req.text, "lxml")
    js = base.text
    store_data = json.loads(js)

    for store in store_data:
        final_link = "https://www.fountaintire.com/stores/details/" + store["id"]
        locator_domain = "fountaintire.com"

        location_name = store["branchName"]
        street_address = store["address"]
        city = store["city"].upper()
        state = store["province"]
        zip_code = store["postalCode"]
        country_code = "CA"
        store_number = store["id"]
        location_type = "<MISSING>"
        phone = store["phoneNumber"]

        hours_of_operation = ""
        raw_hours = store["deserializedHours"]
        days = ["Mon:", "Tue:", "Wed:", "Thu:", "Fri:", "Sat:", "Sun:"]

        for i, hours in enumerate(raw_hours):
            hours_of_operation = (
                hours_of_operation + " " + days[i] + " " + hours
            ).strip()

        latitude = store["lat"]
        longitude = store["lng"]

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url=final_link,
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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
