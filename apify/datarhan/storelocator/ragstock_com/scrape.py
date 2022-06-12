from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()
    domain = "ragstock.com"
    start_url = "https://ragstock.com/stores/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36",
    }

    response = session.get(start_url, headers=headers)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//a[contains(text(), "View Store")]/@href')
    for page_url in all_locations:
        if "http" not in page_url:
            page_url = "https://ragstock.com" + page_url
        loc_response = session.get(page_url, headers=headers)
        loc_dom = etree.HTML(loc_response.text)
        location_type = ""
        temp_closed = loc_dom.xpath('//span[contains(text(), "Temporarily closed")]')
        if temp_closed:
            location_type = "Temporarily closed"
        location_name = loc_dom.xpath("//h1/text()")[0]
        raw_data = loc_dom.xpath("//div[h3[strong]]/p[1]/text()")
        raw_address = ", ".join(
            [e for e in raw_data if not e.startswith("(") and "am-" not in e]
        )
        phone = [e.strip() for e in raw_data if e.startswith("(")]
        phone = phone[0] if phone else ""
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += ", " + addr.street_address_2
        hoo = loc_dom.xpath('//p[strong[contains(text(), "Open:")]]/text()')
        hoo = " ".join([e.strip() for e in hoo if e.strip()])
        if phone:
            hoo = hoo.split(phone)[-1]
        geo = loc_dom.xpath("//iframe/@data-src")
        if not geo:
            geo = loc_dom.xpath('//iframe[contains(@src, "google.com/maps")]/@src')
        geo = geo[0].split("!2d")[-1].split("!3m")[0].split("!3d")

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=addr.city,
            state=addr.state,
            zip_postal=addr.postcode,
            country_code="",
            store_number="",
            phone=phone,
            location_type=location_type,
            latitude=geo[1].split("!")[0],
            longitude=geo[0],
            hours_of_operation=hoo,
            raw_address=raw_address,
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
