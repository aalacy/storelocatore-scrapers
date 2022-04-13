import json

from bs4 import BeautifulSoup

from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

from sgrequests import SgRequests

from sgzip.dynamic import DynamicZipSearch, SearchableCountries

session = SgRequests()


def fetch_data(sgw: SgWriter):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    }

    locator_domain = "https://www.airgas.com/"

    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_search_distance_miles=100,
        expected_search_radius_miles=100,
        max_search_results=20,
    )

    found = []
    for postcode in search:
        base_link = (
            "https://maps.locations.airgas.com/api/getAsyncLocations?template=search&level=search&search="
            + str(postcode)
        )

        r = session.get(
            base_link,
            headers=headers,
        )

        location_list = r.json()["markers"]
        if not location_list:
            continue
        for store_data in location_list:
            store_details = json.loads(BeautifulSoup(store_data["info"], "lxml").text)
            link = store_details["url"]
            if link in found:
                continue
            found.append(link)

            location_name = store_details["location_name"]
            street_address = (
                store_details["address_1"] + " " + store_details["address_2"]
            ).strip()
            city = store_details["city"]
            state = store_details["region"]
            zip_code = store_details["post_code"]
            country_code = store_details["country"]

            store_number = store_details["lid"]

            location_type = ""
            spec = store_data["specialties"]
            for row in spec:
                location_type = location_type + ", " + row["name"]
            location_type = location_type[1:].strip()

            latitude = store_data["lat"]
            longitude = store_data["lng"]
            search.found_location_at(latitude, longitude)

            phone = ""
            hours_of_operation = ""

            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")

            try:
                phone = base.find(class_="phone").text.strip()
            except:
                pass
            try:
                hours_of_operation = " ".join(
                    list(base.find(class_="hours").stripped_strings)
                )
            except:
                pass

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
