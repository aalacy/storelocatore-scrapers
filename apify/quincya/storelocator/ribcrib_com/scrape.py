from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    base_link = (
        "https://api.storerocket.io/api/user/6wgpr528XB/locations?radius=20&units=miles"
    )

    session = SgRequests()
    stores = session.get(base_link, headers=headers).json()["results"]["locations"]

    locator_domain = "ribcrib.com"

    for store in stores:
        location_name = store["name"]
        try:
            street_address = (
                store["address_line_1"] + " " + store["address_line_2"]
            ).strip()
        except:
            street_address = store["address_line_1"].strip()

        if not street_address[:1].isdigit():
            street_address = store["display_address"].split(",")[0]

        city = store["city"]
        state = store["state"]
        zip_code = store["postcode"]
        country_code = "US"
        store_number = store["id"]
        location_type = "<MISSING>"
        phone = store["phone"]

        try:
            hours_of_operation = ""
            raw_hours = store["hours"]
            for hour in raw_hours:
                hours_of_operation = (
                    hours_of_operation + " " + hour + " " + raw_hours[hour]
                ).strip()
        except:
            hours_of_operation = ""
        latitude = store["lat"]
        longitude = store["lng"]
        link = "https://ribcrib.com/locations/?location=" + store["slug"]

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
