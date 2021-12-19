from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.lexus.com.sa/api/teasers/GetDealersAndLocations/%7B1D8E6DC3-C667-47E6-8440-73E075B03B37%7D"
    domain = "lexus.com.sa"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    data = session.get(start_url, headers=hdr).json()

    for poi in data["locations"]:
        phone = etree.HTML(poi["phone"]).xpath("//a/text()")[0]
        hoo = etree.HTML(poi["time"]).xpath("//text()")[1]
        location_type = poi["subtitle"]
        if "Sales" not in location_type:
            continue

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.lexus.com.sa/en/Locate-Lexus-Center#",
            location_name=poi["title"],
            street_address="",
            city="",
            state="",
            zip_postal="",
            country_code="SA",
            store_number="",
            phone=phone,
            location_type=location_type,
            latitude=poi["latitude"],
            longitude=poi["longitude"],
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
