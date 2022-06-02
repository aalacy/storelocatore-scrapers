from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    base_link = "https://paisanospizza.com/wp-json/foodtec/v1/query/stores?lat=38.78185418400665&lng=-77.18659629956237&t=0.2704612493092069"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    items = session.get(base_link, headers=headers).json()["items"]

    for item in items:
        locator_domain = "https://paisanospizza.com"
        location_name = item["name"]
        street_address = item["address"]
        city = item["city"].replace(", DC", "")
        state = item["state"]
        zip_code = item["zip"]
        country_code = "US"
        store_number = "<MISSING>"
        phone = item["telephone"]
        location_type = "<MISSING>"

        hours = item["storeHours"]["any"]
        hours_of_operation = ""
        for row in hours:
            day = row["day"].title()
            hour = row["intervalTm"]
            hours_of_operation = (hours_of_operation + " " + day + " " + hour).strip()

        latitude = item["lat"]
        longitude = item["lng"]
        link = item["baseUrl"]

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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
    fetch_data(writer)
