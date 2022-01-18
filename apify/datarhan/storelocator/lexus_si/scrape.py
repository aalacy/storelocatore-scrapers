from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.lexus.si/contact/dealers/list"
    domain = "lexus.si"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//a[@data-gt-action="view-dealer"]/@href')
    for page_url in all_locations:
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath("//p/b/text()")[0]
        raw_address = loc_dom.xpath('//div[@class="cmp-text "]/p/text()')[1:3]
        raw_address = [e.strip() for e in raw_address]
        phone = (
            loc_dom.xpath('//p[b[contains(text(), "VAŠ PRODAJNI SVETOVALEC")]]/text()')[
                1
            ]
            .split("T:")[-1]
            .strip()
        )
        hoo = loc_dom.xpath('//div[@class="cmp-text "]/p/text()')[4:6]
        hoo = " ".join([e.strip() for e in hoo])

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=raw_address[0],
            city=raw_address[-1].split()[1],
            state="",
            zip_postal=raw_address[-1].split()[0],
            country_code="SI",
            store_number="",
            phone=phone,
            location_type="",
            latitude="",
            longitude="",
            hours_of_operation=hoo,
            raw_address=", ".join(raw_address),
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
