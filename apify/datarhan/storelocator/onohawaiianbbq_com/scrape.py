import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


def fetch_data():
    session = SgRequests()
    domain = "onohawaiianbbq.com"
    start_url = "https://onohawaiianbbq.com/wp-admin/admin-ajax.php?action=store_search&lat={}&lng={}&max_results=100&search_radius=50"
    hdr = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:94.0) Gecko/20100101 Firefox/94.0",
        "Accept": "*/*",
        "X-Requested-With": "XMLHttpRequest",
    }
    all_coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=50
    )
    for lat, lng in all_coords:
        response = session.get(start_url.format(lat, lng), headers=hdr)
        data = json.loads(response.text)

        for poi in data:
            store_url = poi["permalink"]
            store_url = store_url if store_url else "<MISSING>"
            location_name = poi["store"].replace("&#8211;", "-")
            street_address = poi["address"]
            street_address = street_address if street_address else "<MISSING>"
            city = poi["city"]
            city = city if city else "<MISSING>"
            state = poi["state"]
            state = state if state else "<MISSING>"
            zip_code = poi["zip"]
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = poi["country"]
            country_code = country_code if country_code else "<MISSING>"
            store_number = poi["id"]
            phone = poi["phone"]
            phone = phone if phone else "<MISSING>"
            location_type = "<MISSING>"
            latitude = poi["lat"]
            latitude = latitude if latitude else "<MISSING>"
            longitude = poi["lng"]
            longitude = longitude if longitude else "<MISSING>"
            hours_of_operation = ""
            if poi["hours"]:
                hours_of_operation = etree.HTML(poi["hours"])
                hours_of_operation = hours_of_operation.xpath(".//text()")
                hours_of_operation = [
                    elem.strip() for elem in hours_of_operation if elem.strip()
                ]
            hours_of_operation = (
                " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
            )

            if "closed" in hours_of_operation.lower():
                location_type = "closed"
            if "soon" in location_name.lower():
                location_type = "coming soon"

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
