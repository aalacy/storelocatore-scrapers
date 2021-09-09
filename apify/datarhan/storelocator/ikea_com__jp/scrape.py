from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)
    start_url = "https://www.ikea.com/jp/en/stores/"
    domain = "ikea.com/jp"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//pub-hide-empty-link//a[contains(@href, "/stores/")]/@href'
    )[1:]
    for page_url in all_locations:
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath("//h1/text()")[0]
        raw_adr = loc_dom.xpath('//p[strong[contains(text(), "Adress")]]/text()')
        if not raw_adr:
            raw_adr = loc_dom.xpath('//p[strong[contains(text(), "Address")]]/text()')
        if not raw_adr:
            raw_adr = loc_dom.xpath(
                '//p[strong[contains(text(), "Address")]]/following-sibling::p[1]/text()'
            )
        raw_adr = ", ".join(raw_adr)
        addr = parse_address_intl(raw_adr)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        geo = (
            loc_dom.xpath("//iframe/@src")[0]
            .split("!2d")[-1]
            .split("!2m")[0]
            .split("!3d")
        )
        hoo = loc_dom.xpath(
            '//p[strong[contains(text(), "Store opening hours")]]/following-sibling::p/text()'
        )
        hoo = " ".join(hoo).split("“Swedish")[0].strip()

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=addr.city,
            state=addr.state,
            zip_postal=addr.postcode,
            country_code=addr.country,
            store_number="",
            phone="",
            location_type="",
            latitude=geo[1],
            longitude=geo[0],
            hours_of_operation=hoo,
            raw_address=raw_adr,
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
