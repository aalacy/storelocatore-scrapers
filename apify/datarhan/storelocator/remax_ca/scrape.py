import json
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


def fetch_data():
    session = SgRequests()
    domain = "remax.ca"
    start_url = "https://www.remax.ca/api/v1/office/search/?from=0&size=16&category=Residential&text={}"

    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.CANADA], expected_search_radius_miles=100
    )
    for code in all_codes:
        response = session.get(start_url.format(code.replace(" ", "+")))
        data = json.loads(response.text)
        all_locations = data["result"]["results"]

        for poi in all_locations:
            page_url = urljoin("https://www.remax.ca", poi["detailUrl"])
            location_name = poi["officeName"]
            street_address = poi["address1"]
            if poi.get("address2"):
                street_address += " " + poi["address2"]
            city = poi["city"]
            state = poi["state"]
            zip_code = poi["postalCode"]
            country_code = poi["country"]
            store_number = "<MISSING>"
            phone = poi.get("telephone")
            location_type = "<MISSING>"
            latitude = poi["latitude"]
            longitude = poi["longitude"]

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
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
                hours_of_operation="",
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
