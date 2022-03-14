from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgzip.dynamic import DynamicZipSearch, SearchableCountries


def fetch_data(sgw: SgWriter):
    session = SgRequests()
    headers = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    }
    locator_domain = "barnesandnoble.com"

    search = DynamicZipSearch(
        country_codes=[
            SearchableCountries.USA,
        ],
        max_search_distance_miles=50,
        expected_search_radius_miles=50,
    )

    for postcode in search:
        base_link = (
            "https://stores.barnesandnoble.com/_next/data/ljiqyYqTybLw6ZMrfqsEX/index.json?searchText=%s"
            % postcode
        )
        try:
            stores = session.get(base_link, headers=headers).json()["pageProps"][
                "stores"
            ]["content"]
        except:
            continue

        for loc in stores:
            lat = loc["latitude"]
            longit = loc["longitude"]
            search.found_location_at(lat, longit)

            location_name = loc["name"]
            try:
                street_address = loc["address2"].strip()
                raw_address = (loc["address1"] + " " + loc["address2"]).strip()
            except:
                street_address = loc["address1"].strip()
                raw_address = street_address
            city = loc["city"]
            state = loc["state"]
            zip_code = loc["zip"]
            country_code = "US"
            phone_number = loc["phone"]
            store_number = loc["storeId"]
            page_url = "https://stores.barnesandnoble.com/store/" + str(store_number)
            location_type = "<MISSING>"
            try:
                hours = loc["hours"]
            except:
                hours = ""

            sgw.write_row(
                SgRecord(
                    locator_domain=locator_domain,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip_code,
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone_number,
                    location_type=location_type,
                    latitude=lat,
                    longitude=longit,
                    hours_of_operation=hours,
                    raw_address=raw_address,
                )
            )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
