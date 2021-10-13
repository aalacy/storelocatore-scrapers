from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.thecornishbakery.com/wp-admin/admin-ajax.php?action=store_search&lat=50.152571&lng=-5.06627&max_results=25&search_radius=50&autoload=1"
    domain = "thecornishbakery.com"
    response = session.get("https://www.thecornishbakery.com/wish-you-were-here/")
    dom = etree.HTML(response.text)
    all_hoo = dom.xpath(
        '//div[div[div[h1[contains(text(), "Opening Times")]]]]/following-sibling::div[1]//text()'
    )
    all_hoo = [e.strip() for e in all_hoo]

    all_locations = session.get(start_url).json()
    for poi in all_locations:
        location_name = poi["store"]
        street_address = poi["address"]
        if poi["address2"]:
            street_address += " " + poi["address2"]
        hoo = [e.strip() for e in all_hoo if location_name in e]
        hoo = hoo[0].split(": ")[-1] if hoo else ""

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.thecornishbakery.com/wish-you-were-here/",
            location_name=location_name,
            street_address=street_address,
            city=poi["city"],
            state=poi["state"],
            zip_postal=poi["zip"],
            country_code=poi["country"],
            store_number=poi["id"],
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
