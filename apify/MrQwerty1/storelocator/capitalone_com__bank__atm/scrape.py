import json
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch


def fetch_data(la, ln, sgw: SgWriter):
    data = {
        "variables": {
            "input": {
                "lat": float(la),
                "long": float(ln),
                "radius": 25,
                "locTypes": ["atm"],
                "servicesFilter": [],
            }
        },
        "query": "\n        query geoSearch($input: GeoSearchInput!){\n          geoSearch(input: $input){\n            locType\n            locationName\n            locationId\n            address {\n              addressLine1\n              stateCode\n              postalCode\n              city\n            }\n            services\n            distance\n            latitude\n            longitude\n            slug\n            seoType\n            ... on Atm {\n              open24Hours\n            }\n            ... on Branch {\n              phoneNumber\n              timezone\n              lobbyHours {\n                day\n                open\n                close\n              }\n              driveUpHours {\n                day\n                open\n                close\n              }\n              temporaryMessage\n              reopenDate\n            }\n            ... on Cafe {\n              phoneNumber\n              photo\n              timezone\n              hours {\n                day\n                open\n                close\n              }\n              temporaryMessage\n              reopenDate\n            }\n          }\n        }",
    }

    r = session.post(
        "https://api.capitalone.com/locations", headers=headers, data=json.dumps(data)
    )
    js = r.json()["data"]["geoSearch"]

    for j in js:
        a = j.get("address")
        street_address = (
            f"{a.get('addressLine1')} {a.get('addressLine2') or ''}".strip()
        )
        city = a.get("city")
        state = a.get("stateCode")
        postal = a.get("postalCode")
        country_code = "US"
        store_number = j.get("locationId")
        page_url = f'https://locations.capitalone.com/-/-/{j.get("slug")}'
        location_name = j.get("locationName")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        location_type = j.get("locType")

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            location_type=location_type,
            latitude=str(latitude),
            longitude=str(longitude),
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Accept": "application/json;v=1",
        "Accept-Language": "uk-UA,uk;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/json",
        "Origin": "https://locations.capitalone.com",
        "Connection": "keep-alive",
        "Referer": "https://locations.capitalone.com/",
    }
    locator_domain = "https://www.capitalone.com/bank/atm/"
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=25
    )
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.PageUrlId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        for lat, lng in search:
            fetch_data(lat, lng, writer)
