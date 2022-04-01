import json
from lxml import etree
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "braums.com"
    start_url = "https://www.braums.com/wp-admin/admin-ajax.php?action=store_search&lat={}&lng={}&max_results=100&search_radius=100"

    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }
    all_coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        expected_search_radius_miles=100,
    )
    for lat, lng in all_coords:
        response = session.get(
            start_url.format(str(lat)[:8], str(lng)[:9]), headers=headers
        )
        data = json.loads(response.text)

        for poi in data:
            store_url = poi["permalink"]
            location_name = poi["store"]
            street_address = poi["address"]
            if poi["address2"]:
                street_address += ", " + poi["address2"]
            city = poi["city"]
            state = poi["state"]
            zip_code = poi["zip"]
            country_code = poi["country"]
            store_number = poi["id"]
            phone = poi["phone"]
            latitude = poi["lat"]
            longitude = poi["lng"]
            hours_of_operation = ""
            if poi["hours"]:
                hours_of_operation = etree.HTML(poi["hours"])
                hours_of_operation = hours_of_operation.xpath("//td//text()")
            hours_of_operation = (
                " ".join(hours_of_operation) if hours_of_operation else ""
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
