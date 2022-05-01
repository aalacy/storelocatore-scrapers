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
    start_url = "https://stockist.co/api/v1/u2561/locations/search?callback=jQuery214013437323466009143_1617278571042&tag=u2561&latitude={}&longitude={}&filters%5B%5D=711&distance=250"
    domain = "morphe.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    all_coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA, SearchableCountries.CANADA],
        max_search_distance_miles=200,
    )
    for lat, lng in all_coords:
        response = session.get(start_url.format(lat, lng), headers=hdr)
        data = re.findall(
            r"jQuery214013437323466009143_1617278571042\((.+)\);", response.text
        )[0]
        data = json.loads(data)
        all_locations = data["locations"]

        for poi in all_locations:
            page_url = "https://www.morphe.com/pages/store-locator"
            location_name = poi["name"]
            street_address = poi["address_line_1"]
            if poi["address_line_2"]:
                street_address += " " + poi["address_line_2"]
            city = poi["city"]
            state = poi["state"]
            zip_code = poi["postal_code"]
            if zip_code and len(zip_code) < 3:
                zip_code = ""
            country_code = poi["country"]
            store_number = poi["id"]
            phone = poi["phone"]
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
                location_type="",
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
            ),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
