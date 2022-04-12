from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.altabank.com/_/api/branches/40.3771253/-111.7978905/500"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    store_data = session.get(base_link, headers=headers).json()["branches"]

    locator_domain = "https://www.altabank.com"

    for store in store_data:
        location_name = store["name"]
        street_address = store["address"]
        city = store["city"]
        state = store["state"]
        if city == "Preston":
            state = "ID"
        zip_code = store["zip"]
        country_code = "US"
        store_number = ""
        phone = store["phone"]
        location_type = ""
        latitude = store["lat"]
        longitude = store["long"]

        raw_data = BeautifulSoup(store["description"], "lxml")
        rows = list(raw_data.stripped_strings)
        hours_of_operation = ""

        for row in rows:
            if "lobby" in row.lower():
                hours_of_operation = (
                    hours_of_operation + " " + row.split("(")[0]
                ).strip()

        link = raw_data.find_all("a")[-1]["href"]

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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
