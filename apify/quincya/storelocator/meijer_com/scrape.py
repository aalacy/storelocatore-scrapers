from sglogging import SgLogSetup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

from sgzip.dynamic import DynamicZipSearch, SearchableCountries

log = SgLogSetup().get_logger("meijer.com")


def fetch_data(sgw: SgWriter):
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    max_distance = 100

    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_search_distance_miles=max_distance,
        expected_search_radius_miles=max_distance,
        max_search_results=10,
    )

    locator_domain = "meijer.com"

    for postcode in search:
        base_link = (
            "https://www.meijer.com/bin/meijer/store/search?locationQuery=%s&radius=%s"
            % (postcode, max_distance)
        )

        log.info(base_link)
        stores = session.get(base_link, headers=headers).json()["pointsOfService"]
        for store in stores:
            location_name = store["displayName"]
            street_address = store["address"]["line1"].strip()
            city = store["address"]["town"]
            state = store["address"]["region"]["isocode"].replace("US-", "")
            zip_code = store["address"]["postalCode"]
            country_code = "US"
            latitude = store["geoPoint"]["latitude"]
            longitude = store["geoPoint"]["longitude"]
            search.found_location_at(latitude, longitude)
            store_number = store["name"]
            location_type = "<MISSING>"
            phone = store["phone"]
            hours_of_operation = "<INACCESSIBLE>"
            link = "<MISSING>"

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
