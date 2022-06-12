from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


def fetch_data():
    session = SgRequests()
    domain = "freshii.com"

    start_url = "https://bff-avokado.freshii.com/graphql"
    all_coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA, SearchableCountries.CANADA],
        expected_search_radius_miles=500,
    )
    for lat, lng in all_coords:
        frm = {
            "operationName": "getLocations",
            "variables": {
                "input": {
                    "northEast": {
                        "latitude": lat,
                        "longitude": lng,
                    },
                    "southWest": {
                        "latitude": lat - 10.0,
                        "longitude": lng + 10.0,
                    },
                    "distanceFrom": {"latitude": lat + 5.0, "longitude": lng + 5.0},
                    "handoffMode": "PICKUP",
                    "offset": 0,
                    "limit": 500,
                }
            },
            "query": "query getLocations($input: LocationFilter) {\n  getLocations(input: $input) {\n    id\n    name\n    storeName\n    streetAddress\n    city\n    state\n    country\n    telephone\n    zipCode\n    latitude\n    longitude\n    utcOffset\n    hours {\n      baseHours {\n        day\n        endDay\n        hourFrom\n        hourFromSuffix\n        hourTo\n        hourToSuffix\n        handoffMode\n      }\n    }\n    distance {\n      value\n      unit\n    }\n  }\n}\n",
        }

        hdr = {
            "accept": "*/*",
            "authorization": "",
            "content-type": "application/json",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
        }

        data = session.post(start_url, headers=hdr, json=frm).json()
        all_locations = data["data"]["getLocations"]
        if not all_locations:
            all_coords.found_nothing()
            continue
        all_coords.found_location_at(lat, lng)
        for poi in all_locations:
            hoo = []
            for e in poi["hours"]["baseHours"]:
                day = e["day"]
                opens = f"{e['hourFrom']} {e['hourFromSuffix']}"
                closes = f"{e['hourTo']} {e['hourToSuffix']}"
                hoo.append(f"{day}: {opens} - {closes}")
            hoo = " ".join(hoo)

            item = SgRecord(
                locator_domain=domain,
                page_url="https://orders.freshii.com/en/stores",
                location_name=poi["name"],
                street_address=poi["streetAddress"],
                city=poi["city"],
                state=poi["state"],
                zip_postal=poi["zipCode"],
                country_code=poi["country"],
                store_number="",
                phone=poi["telephone"],
                location_type="",
                latitude=poi["latitude"],
                longitude=poi["longitude"],
                hours_of_operation=hoo,
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
