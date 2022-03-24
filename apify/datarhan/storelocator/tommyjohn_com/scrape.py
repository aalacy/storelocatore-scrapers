from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://tommyjohn.com/pages/store-directory"
    domain = "tommyjohn.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="address stores-section"]')
    for poi_html in all_locations:
        raw_address = poi_html.xpath(
            './/p[@class="stores-section__content-section stores-section__content-address"]/text()'
        )
        raw_address = [e.strip() for e in raw_address]
        location_name = poi_html.xpath(".//h2/text()")[0]
        phone = poi_html.xpath(
            './/p[@class="stores-section__content-section stores-section__content-phone"]/a/text()'
        )[0]
        raw_hoo = poi_html.xpath(".//p/text()")
        raw_hoo = [e.strip() for e in raw_hoo if "PM" in e]
        hoo = " ".join(raw_hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=raw_address[0],
            city=raw_address[1].split(", ")[0],
            state=raw_address[1].split(", ")[-1].split()[0],
            zip_postal=raw_address[1].split(", ")[-1].split()[-1],
            country_code="",
            store_number="",
            phone=phone,
            location_type="",
            latitude="",
            longitude="",
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
