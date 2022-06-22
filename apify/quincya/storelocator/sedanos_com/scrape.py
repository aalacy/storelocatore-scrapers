from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    base_link = "https://api.freshop.com/1/stores?app_key=sedanos&has_address=true&is_selectable=true&limit=-1&token=ff01a1a393d43dd6b06c6a49777a0931"

    session = SgRequests()
    stores = session.get(base_link, headers=headers).json()["items"]

    locator_domain = "http://sedanos.com/"

    for store in stores:
        location_name = store["name"]
        street_address = store["address_1"]
        city = store["city"]
        state = store["state"]
        zip_code = store["postal_code"]
        country_code = "US"
        store_number = store["id"]
        location_type = "<MISSING>"
        phone = store["phone"].replace("Storer", "Store").split("ore:")[-1].strip()
        hours_of_operation = store["hours_md"].replace("\n", " ")
        latitude = store["latitude"]
        longitude = store["longitude"]
        link = store["url"]

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
