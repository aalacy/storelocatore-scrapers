import json
from urllib.parse import urljoin
from w3lib.url import add_or_replace_parameter

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


def fetch_data():
    session = SgRequests()
    domain = "traction.com"
    start_url = "https://www.traction.com/en/store-finder?q={}&page=0"

    session.get(start_url)
    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.CANADA], expected_search_radius_miles=200
    )
    for code in all_codes:
        code_url = start_url.format(code)
        response = session.get(code_url)
        try:
            data = json.loads(response.text)
        except Exception:
            continue
        all_locations = data["data"]
        if data["total"] > 10:
            total_pages = data["total"] // 10 + 1
            for page in range(1, total_pages):
                page_url = add_or_replace_parameter(code_url, "page", str(page))
                response = session.get(page_url)
                try:
                    data = json.loads(response.text)
                    all_locations += data["data"]
                except Exception:
                    continue

        for poi in all_locations:
            store_url = urljoin(
                "https://www.traction.com",
                poi["url"]
                .replace(" ", "-")
                .replace("(", "")
                .replace(")", "")
                .replace(".", ""),
            ).split("?")[0]
            location_name = poi["name"].replace("&#039;", "'")
            street_address = poi["line1"]
            city = poi["town"]
            state = poi["region"]
            zip_code = poi["postalCode"]
            country_code = "CA"
            store_number = poi["storeId"]
            phone = poi["phone"]
            latitude = poi["latitude"]
            longitude = poi["longitude"]
            hoo = []
            for day, hours in poi["openings"].items():
                hoo.append(f"{day} {hours}")
            hours_of_operation = " ".join(hoo) if hoo else ""

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
                location_type="",
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
