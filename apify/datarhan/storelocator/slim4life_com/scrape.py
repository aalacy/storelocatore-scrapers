from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://slim4life.com/locations/"
    domain = "slim4life.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//a[contains(text(), "Click here for more info")]/@href')
    for page_url in all_locations:
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath("//h2/strong/text()")[0].strip()
        raw_address = loc_dom.xpath('//div[@class="et_pb_text_inner"]/p[1]/text()')[0]
        addr = parse_address_intl(raw_address)
        phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')[1]
        geo = (
            loc_dom.xpath("//iframe/@src")[0]
            .split("!2d")[-1]
            .split("!2m")[0]
            .split("!3d")
        )
        hoo = loc_dom.xpath(
            '//h2[contains(text(), "Center Hours of Operation:")]/following-sibling::ul/li//text()'
        )[:-1]
        hoo = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=raw_address.split(", ")[0],
            city=addr.city,
            state=addr.state,
            zip_postal=addr.postcode,
            country_code="",
            store_number="",
            phone=phone,
            location_type="",
            latitude=geo[1].split("!")[0],
            longitude=geo[0],
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
