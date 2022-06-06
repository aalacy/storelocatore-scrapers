from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    locator_domain = "walk-ons.com"

    store_link = (
        "https://go.walk-ons.com/wp-content/themes/astra-child/assets/js/data.json"
    )

    stores = session.get(store_link, headers=headers).json()

    for store in stores:
        if store["coming_soon"] == "1":
            continue
        location_name = store["friendlyName"]
        street_address = store["address"]
        city = store["city"]
        state = store["state"]
        zip_code = store["zipCode"]
        country_code = "US"
        store_number = store["id"]
        location_type = ""
        phone = store["contact_number"]
        hours_of_operation = store["days_hours"].replace("<br/>", " ")
        latitude = store["lat"]
        longitude = store["lon"]
        link = "https://go.walk-ons.com" + store["locationLink"]

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
