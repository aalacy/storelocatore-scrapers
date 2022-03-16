import re

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


def fetch_data():
    session = SgRequests()
    domain = "optumcare.com"
    actions = [
        "search-urgent-care",
        "search-hospitals",
        "search-labs",
        "search-facilities",
    ]
    all_coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=50
    )
    for lat, lng in all_coords:
        for action in actions:
            url = "https://lookup.optumcare.com/locations-results/?lat={}&lng={}&action={}&side=1&location-office-zip=&radius=50"
            response = session.get(url.format(lat, lng, action))
            all_locations = re.findall(r"d_object\((.+?)\);", response.text)
            for poi in all_locations:
                poi = [e.replace('"', "") for e in poi.split(",")]
                if len(poi) == 13:
                    del poi[2]
                page_url = "https://lookup.optumcare.com" + poi[10]
                if "location-details" not in page_url:
                    print(poi)
                    page_url = "https://lookup.optumcare.com" + poi[11]

                item = SgRecord(
                    locator_domain=domain,
                    page_url=page_url,
                    location_name=poi[1],
                    street_address=poi[3],
                    city=poi[4],
                    state=poi[5],
                    zip_postal=poi[6],
                    country_code="",
                    store_number=poi[0],
                    phone=poi[2],
                    location_type="",
                    latitude=poi[7],
                    longitude=poi[8],
                    hours_of_operation="",
                )

                yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            ),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
