from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    start_url = "https://bemobile.com/locations/"
    domain = "bemobile.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="state"]//strong/a/@href')
    for page_url in all_locations:
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)
        location_name = loc_dom.xpath("//h1/text()")[0]
        raw_adr = loc_dom.xpath("//address/text()")
        raw_adr = [e.strip() for e in raw_adr if e.strip()]
        street_address = raw_adr[0].strip()
        if street_address.endswith(","):
            street_address = street_address[:-1]
        phone = loc_dom.xpath(
            '//i[@class="fa fa-mobile"]/following-sibling::strong/text()'
        )[0]
        hoo = loc_dom.xpath('//p[@class="hours"]/text()')
        hoo = " ".join([e.strip() for e in hoo if e.strip()])

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=raw_adr[-1].split(", ")[0],
            state=raw_adr[-1].split(", ")[-1].split()[0],
            zip_postal=raw_adr[-1].split(", ")[-1].split()[-1],
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
