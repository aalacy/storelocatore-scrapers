from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sglogging import SgLogSetup

from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

logger = SgLogSetup().get_logger("bcf.com.au")


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    locator_domain = "https://www.bcf.com.au/"
    coords = DynamicGeoSearch(
        country_codes=[
            SearchableCountries.AUSTRALIA,
        ],
        max_search_distance_miles=100,
    )

    found = []
    for lat, lon in coords:
        base_link = (
            "https://www.bcf.com.au/on/demandware.store/Sites-bcf-au-Site/en_AU/Stores-SearchPost?lat=%s&lng=%s&countryCode=AU"
            % (lat, lon)
        )
        stores = session.post(base_link, headers).json()["stores"]

        for store in stores:
            location_name = store["name"]
            street_address = (store["address1"] + " " + store["address2"]).strip()
            city = store["city"]
            state = store["stateCode"]
            zip_code = store["postalCode"]
            country_code = store["countryCode"]
            location_type = ""
            phone = store["phone"]
            hours_of_operation = ""
            store_number = ""
            latitude = store["latitude"]
            longitude = store["longitude"]
            link = store["storeDetailURL"]
            if link not in found:
                logger.info(link)
                found.append(link)
                req = session.get(link, headers=headers)
                base = BeautifulSoup(req.text, "lxml")
                hours_of_operation = " ".join(
                    list(base.find(class_="opening-hours").stripped_strings)
                )

            coords.found_location_at(lat, lon)

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
