import json
from w3lib.url import add_or_replace_parameter
from sgzip.dynamic import DynamicZipSearch, SearchableCountries

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "jared.com"

    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        expected_search_radius_miles=50,
    )

    for code in all_codes:
        url = "https://www.jared.com/store-finder/find?q={}&page=0".format(code)
        response = session.get(url)
        data = json.loads(response.text)
        if not data.get("data"):
            continue
        all_locations = data["data"]
        if data["total"] > 5:
            for page in range(1, data["total"] // 5 + 2):
                page_url = add_or_replace_parameter(url, "page", str(page))
                response = session.get(page_url)
                data = json.loads(response.text)
                if not data.get("data"):
                    continue
                all_locations += data["data"]

        for poi in all_locations:
            page_url = url
            if "null" not in poi["url"]:
                page_url = "https://www.jared.com" + poi["url"]
            location_name = poi["displayName"]
            street_address = poi["line1"]
            if poi["line2"]:
                street_address += ", " + poi["line2"]
            city = poi["town"]
            state = poi["regionIsoCodeShort"]
            zip_code = poi["postalCode"]
            country_code = "<MISSING>"
            store_number = poi["name"]
            phone = poi["phone"]
            latitude = poi["latitude"]
            longitude = poi["longitude"]
            hours_of_operation = []
            for day, hours in poi["openings"].items():
                hours_of_operation.append(f"{day} {hours}")
            hours_of_operation = (
                " ".join(hours_of_operation) if hours_of_operation else ""
            )

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
