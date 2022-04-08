from bs4 import BeautifulSoup

from sglogging import sglog

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

log = sglog.SgLogSetup().get_logger(logger_name="kumandgo.com")


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    session1 = SgRequests()

    locator_domain = "kumandgo.com"

    found = []
    max_distance = 500
    max_results = 100

    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        max_search_distance_miles=max_distance,
        max_search_results=max_results,
    )

    for lat, lng in search:
        log.info(
            "Searching: %s, %s | Items remaining: %s"
            % (lat, lng, search.items_remaining())
        )

        base_link = (
            "https://www.kumandgo.com/wordpress/wp-admin/admin-ajax.php?action=store_search&lat=%s&lng=%s&max_results=100&search_radius=%s"
            % (lat, lng, max_distance)
        )
        stores = session.get(base_link, headers=headers).json()

        for store in stores:
            location_name = "KUM & GO #" + store["store"]
            street_address = store["address"]
            city = store["city"]
            state = store["state"]
            zip_code = store["zip"]
            country_code = store["country"]
            store_number = store["store"]
            phone = store["phone"]
            hours_of_operation = store["hours"]
            if not hours_of_operation:
                hours_of_operation = "<MISSING>"
            latitude = store["lat"]
            longitude = store["lng"]
            search.found_location_at(float(latitude), float(longitude))

            if store_number in found:
                continue
            found.append(store_number)
            link = store["permalink"]
            req = session1.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")

            location_type = ", ".join(
                list(base.find(class_="no-decoration feature-icons").stripped_strings)
            )

            if "Open 24hrs" in location_type:
                hours_of_operation = "Open 24 Hours"
            hours_of_operation = BeautifulSoup(hours_of_operation, "html.parser")
            hours_of_operation = hours_of_operation.get_text(
                separator="|", strip=True
            ).replace("|", " ")

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
