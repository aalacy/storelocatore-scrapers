from bs4 import BeautifulSoup

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
    locator_domain = "ppgpaints.com"

    search = DynamicZipSearch(
        country_codes=[
            SearchableCountries.USA,
            SearchableCountries.CANADA,
            SearchableCountries.PUERTO_RICO,
        ],
        max_search_distance_miles=50,
        expected_search_radius_miles=50,
        max_search_results=10,
    )
    dup_tracker = []

    for postcode in search:
        base_link = (
            "https://www.ppgpaints.com/store-locator/search?value=%s&latitude=&longitude=&filter=Store"
            % postcode
        )
        stores = session.get(base_link, headers=headers).json()["Items"]

        for loc in stores:

            lat = loc["Latitude"]
            longit = loc["Longitude"]
            search.found_location_at(lat, longit)

            page_url = "https://www.ppgpaints.com" + loc["LocationUrl"]
            if page_url in dup_tracker:
                continue
            dup_tracker.append(page_url)

            location_name = loc["Name"]
            street_address = (
                loc["Street1"]
                + " "
                + loc["Street2"]
                + " "
                + loc["Street3"]
                + " "
                + loc["Street4"]
            ).strip()
            city = loc["City"]
            state = loc["State"]
            zip_code = loc["PostalCode"]
            country_code = "US"
            if state == "PR":
                country_code = "PR"
            if state == "VI":
                country_code = "VI"
            store_number = location_name.split()[-1]
            if not store_number.isdigit():
                store_number = "<MISSING>"
            phone_number = loc["PhoneNumber"]
            location_type = "<MISSING>"

            if "temporarily closed" in location_name.lower():
                hours = "Temporarily Closed"
                store_number = "<MISSING>"
            else:
                req = session.get(page_url, headers=headers)
                base = BeautifulSoup(req.text, "lxml")
                try:
                    hours = " ".join(
                        list(base.find(class_="hours-dropdown").stripped_strings)
                    )
                except:
                    hours = "<MISSING>"

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
                )
            )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
