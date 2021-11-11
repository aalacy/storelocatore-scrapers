import json

from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "uspoloassn.com"
    start_url = "https://uspoloassnglobal.com/stores/location/{},{}/radius/200/lang/en/storeType/"

    all_locations = []
    all_coordinates = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=200
    )
    for lat, lng in all_coordinates:
        response = session.get(start_url.format(lat, lng))
        data = json.loads(response.text)
        if data["response"]:
            all_locations += data["response"]["entities"]

    for poi in all_locations:
        store_url = "<MISSING>"
        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address"]["line1"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["address"]["city"]
        city = city if city else "<MISSING>"
        state = poi["address"]["region"]
        state = state if state else "<MISSING>"
        zip_code = poi["address"]["postalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["address"]["countryCode"]
        if country_code != "US":
            continue
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["meta"]["id"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["mainPhone"]
        phone = phone if phone else "<MISSING>"
        location_type = poi["meta"]["schemaTypes"][0]
        if "Event" in location_type:
            continue
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if poi["displayCoordinate"]:
            latitude = poi["displayCoordinate"]["latitude"]
            longitude = poi["displayCoordinate"]["longitude"]
        hoo = []
        if poi["hours"]:
            for day, hours in poi["hours"].items():
                if hours["isClosed"]:
                    hoo.append(f"{day} closed")
                else:
                    opens = hours["openIntervals"][0]["start"]
                    closes = hours["openIntervals"][0]["end"]
                    hoo.append(f"{day} {opens} - {closes}")
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
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
