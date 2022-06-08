from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "freshii.com"

    start_url = "https://bff-avokado.freshii.com/graphql"
    frm = {
        "operationName": "getLocations",
        "variables": {
            "input": {
                "northEast": {
                    "latitude": 51.82783930427531,
                    "longitude": -43.929211062500016,
                },
                "southWest": {
                    "latitude": 34.51407754366117,
                    "longitude": -114.50538293750002,
                },
                "distanceFrom": {"latitude": 43.793547, "longitude": -79.217297},
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
    for poi in data["data"]["getLocations"]:
        hoo = []
        for e in poi["hours"]["baseHours"]:
            day = e["day"]
            opens = f"{e['hourFrom']} {e['hourFromSuffix']}"
            closes = f"{e['hourTo']} {e['hourToSuffix']}"
            hoo.append(f"{day}: {opens} - {closes}")
        hoo = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url="",
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
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
