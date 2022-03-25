from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://chebahut.com/modules/multilocation/?near_location=Wisconsin&threshold=4000&relevancy_filter=places_city_match&distance_unit=miles&limit=100&services__in=&language_code=en-us&published=1&within_business=true"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    store_data = session.get(base_link, headers=headers).json()["objects"]

    locator_domain = "https://chebahut.com"

    for store in store_data:
        location_name = store["location_name"]
        street_address = store["street"]
        city = store["city"]
        state = store["state"]
        zip_code = store["postal_code"]
        country_code = "US"
        store_number = store["id"]
        try:
            phone = store["phonemap"]["phone"]
        except:
            phone = ""
        location_type = ""
        latitude = store["lat"]
        longitude = store["lon"]

        rows = raw_hours = store["formatted_hours"]["primary"]["grouped_days"]
        hours_of_operation = ""

        for row in rows:
            hours_of_operation = (
                hours_of_operation + " " + row["label_abbr"] + " " + row["content"]
            ).strip()

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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
