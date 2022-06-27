from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    domain = "aibni.co.uk"
    start_url = "https://aibni.co.uk/branchlocator"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//div[@class="card-body p-sm-4 p-md-5"]')
    for poi_html in all_locations:
        store_url = start_url
        location_name = poi_html.xpath(".//h2/b/text()")
        if not location_name:
            location_name = poi_html.xpath(".//h2/text()")
        location_name = location_name[0].strip()
        raw_address = poi_html.xpath('.//div[@class="mb-0"]/p[1]/text()')[0].split(", ")
        if "Meadowbank" in raw_address[0]:
            raw_address = [", ".join(raw_address[:2])] + raw_address[2:]
        phone = (
            poi_html.xpath('.//div[@class="mb-0"]/p[3]/text()')[0]
            .replace(":\xa0", "")
            .strip()
        )
        geo = (
            poi_html.xpath('.//a[contains(@href, "maps")]/@href')[0]
            .split("/@")[-1]
            .split(",")[:2]
        )
        hoo = poi_html.xpath(
            './/h4[contains(text(), "Opening Hours")]/following-sibling::p//text()'
        )
        hoo = [e.replace("\xa0", " ").strip() for e in hoo]

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=raw_address[0],
            city=raw_address[1],
            state=SgRecord.MISSING,
            zip_postal=raw_address[-1],
            country_code=SgRecord.MISSING,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=geo[0],
            longitude=geo[1],
            hours_of_operation=" ".join(hoo),
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
