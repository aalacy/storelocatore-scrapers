import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "juanpollo.com"
    start_url = "https://juanpollo.com/wp-admin/admin-ajax.php?action=store_search&lat=34.12555&lng=-117.29456&max_results=10&search_radius=5&autoload=1"

    response = session.get(start_url)
    all_locations = json.loads(response.text)
    for poi in all_locations:
        hoo = etree.HTML(poi["hours"])
        hoo = [elem.strip() for elem in hoo.xpath("//text()") if elem.strip()]
        hoo = " ".join(hoo) if hoo else ""
        page_url = poi["url"] if poi["url"] else "https://juanpollo.com/locations/"

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["store"],
            street_address=poi["address"],
            city=poi["city"],
            state=poi["state"],
            zip_postal=poi["zip"],
            country_code=poi["country"],
            store_number="",
            phone=poi["phone"],
            location_type="",
            latitude=poi["lat"],
            longitude=poi["lng"],
            hours_of_operation=hoo,
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
