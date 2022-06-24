import json

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


def fetch_data():
    session = SgRequests()
    domain = "allentireco.com"
    start_url = "https://www.allentireco.com/wp-json/monro/v1/stores/coords?latitude={}&longitude={}&distance=500"

    all_coordinates = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        expected_search_radius_miles=500,
    )
    for lat, lng in all_coordinates:
        response = session.get(start_url.format(lat, lng))
        data = json.loads(response.text)
        all_locations = data["data"]
        if not all_locations:
            all_coordinates.found_nothing()

        for poi in all_locations:
            latitude = poi["Latitude"]
            longitude = poi["Longitude"]
            all_coordinates.found_location_at(latitude, longitude)
            hours_of_operation = []
            hoo_dict = {}
            for key, value in poi.items():
                if "OpenTime" in key:
                    day = key.replace("OpenTime", "")
                    opens = value
                    if hoo_dict.get(day):
                        hoo_dict[day]["opens"] = opens
                    else:
                        hoo_dict[day] = {}
                        hoo_dict[day]["opens"] = opens
                if "CloseTime" in key:
                    day = key.replace("CloseTime", "")
                    closes = value
                    if hoo_dict.get(day):
                        hoo_dict[day]["closes"] = closes
                    else:
                        hoo_dict[day] = {}
                        hoo_dict[day]["closes"] = closes

            for day, hours in hoo_dict.items():
                opens = hours["opens"]
                closes = hours["closes"]
                hours_of_operation.append(f"{day} {opens} - {closes}")
            hours_of_operation = (
                ", ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
            )

            item = SgRecord(
                locator_domain=domain,
                page_url="https://www.allentireco.com/store-search/",
                location_name=poi["BrandDisplayName"],
                street_address=poi["Address"],
                city=poi["City"],
                state=poi["StateCode"],
                zip_postal=poi["ZipCode"],
                country_code="",
                store_number=poi["Id"],
                phone=poi["SalesPhone"],
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
