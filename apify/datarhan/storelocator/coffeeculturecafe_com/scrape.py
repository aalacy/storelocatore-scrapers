from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    # Your scraper here
    session = SgRequests()

    domain = "coffeeculturecafe.com"
    start_url = "https://www.coffeeculturecafe.com/locations/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[p[span[@style="font-size: 24px;" and strong]]]')
    for poi_html in all_locations:
        store_url = start_url
        location_name = poi_html.xpath(".//p/span/strong/text()")[0]
        raw_data = poi_html.xpath("p[2]/text()")
        raw_data = [e.strip() for e in raw_data if e.strip()]
        street_address = raw_data[0]
        city = location_name.split(",")[0].strip()
        state = location_name.split(",")[-1].strip()
        phone = raw_data[1].split(":")[-1].strip()
        hoo = poi_html.xpath("p[2]//text()")
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = (
            " ".join(hoo).split(phone)[-1].strip() if hoo else SgRecord.MISSING
        )

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=SgRecord.MISSING,
            country_code=SgRecord.MISSING,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
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
