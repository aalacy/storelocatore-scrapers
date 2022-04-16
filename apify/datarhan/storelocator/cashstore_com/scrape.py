from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


def fetch_data():
    session = SgRequests(verify_ssl=False)
    domain = "cashstore.com"
    start_url = (
        "https://www.cashstore.com/api/v1/stores/search?latitude={}&longitude={}"
    )

    all_coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=20
    )
    for lat, lng in all_coords:
        all_locations = session.get(start_url.format(lat, lng)).json()
        for poi in all_locations:
            page_url = urljoin("https://www.cashstore.com", poi["url"])
            location_name = "Cash Store"
            street_address = poi["address"]
            city = poi["city"]
            state = poi["state"]
            zip_code = poi["zip"]
            store_number = poi["storeNumber"]
            phone = poi["phone"]
            location_type = ""
            if poi["isClosed"]:
                location_type = "closed"
            latitude = poi["latitude"]
            longitude = poi["longitude"]
            hoo = []
            days = [
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
                "sunday",
            ]
            for day in days:
                opens = poi[f"{day}Open"]
                closes = poi[f"{day}Close"]
                hoo.append(f"{day} {opens} - {closes}")
            hours_of_operation = " ".join(hoo) if hoo else ""

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code="",
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
