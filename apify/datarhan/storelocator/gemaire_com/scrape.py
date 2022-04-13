import json

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


def fetch_data():
    session = SgRequests()
    domain = "gemaire.com"
    start_url = "https://www.gemaire.com/branch/service/locate/?address={}"

    all_locations = []
    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        expected_search_radius_miles=200,
    )
    for code in all_codes:
        response = session.get(start_url.format(code))
        data = json.loads(response.text)
        if data.get("branches"):
            all_locations += data["branches"]

    for poi in all_locations:
        if type(poi) == str:
            continue
        location_name = poi["branch_name"]
        street_address = poi["address"]["address_2"]
        if poi["address"]["address_3"]:
            street_address += ", " + poi["address"]["address_3"]
        city = poi["address"]["city"]
        state = poi["address"]["state"]
        zip_code = poi["address"]["postcode"]
        country_code = poi["address"]["country"]
        store_number = poi["branch_id"]
        phone = poi["phone"]
        location_type = "<MISSING>"
        latitude = poi["latitude"]
        longitude = poi["longitude"]
        hours_of_operation = []
        days = {
            "1": "Monday",
            "2": "Tuesday",
            "3": "Wendsday",
            "4": "Thursday",
            "5": "Friday",
            "6": "Satarday",
            "7": "Sunday",
        }
        for day, hours in poi["formatted_hours"].items():
            day = days[day]
            if hours["isOpen"]:
                opens = hours["open"]
                closes = hours["close"]
                hours_of_operation.append(f"{day} {opens} - {closes}")
            else:
                hours_of_operation.append(f"{day} closed")
        hours_of_operation = " ".join(hours_of_operation) if hours_of_operation else ""

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.gemaire.com",
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
