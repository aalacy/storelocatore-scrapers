import re
import json

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


def fetch_data():
    session = SgRequests()
    start_url = "https://stockist.co/api/v1/u6213/locations/search?callback=jQuery2140954745267521351_1616749393059&tag=u6213&latitude={}&longitude={}"
    domain = "aceliquor.ca"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    all_coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.CANADA], expected_search_radius_miles=100
    )
    for lat, lng in all_coords:
        response = session.get(start_url.format(lat, lng), headers=hdr)
        data = re.findall(r"\(({.+})\);", response.text)[0]
        data = json.loads(data)
        all_locations = data["locations"]

        for poi in all_locations:
            store_url = "https://aceliquor.ca/pages/store-locator"
            location_name = poi["name"]
            location_name = location_name if location_name else "<MISSING>"
            street_address = poi["address_line_1"]
            street_address = street_address if street_address else "<MISSING>"
            city = poi["city"]
            city = city if city else "<MISSING>"
            state = poi["state"]
            state = state if state else "<MISSING>"
            zip_code = poi["postal_code"]
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = poi["country"]
            country_code = country_code if country_code else "<MISSING>"
            store_number = poi["id"]
            phone = poi["phone"]
            phone = phone if phone else "<MISSING>"
            location_type = "<MISSING>"
            latitude = poi["latitude"]
            longitude = poi["longitude"]
            hours_of_operation = poi["custom_fields"][0]["value"]
            hours_of_operation = (
                hours_of_operation if hours_of_operation else "<MISSING>"
            )

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
            ),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
