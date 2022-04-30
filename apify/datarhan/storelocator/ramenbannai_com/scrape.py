from lxml import etree

from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://ramenbannai.com/location/"
    domain = "ramenbannai.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="location-box clearfix"]')
    for poi_html in all_locations:
        if poi_html.xpath('.//*[contains(text(), "OPENING SOON")]'):
            continue
        store_url = start_url
        location_name = poi_html.xpath('.//p/span[@class="tenpo"]/text()')[0].split()
        location_name = [e.strip() for e in location_name if e.strip()]
        location_name = " ".join(location_name).replace("â", "-")
        raw_address = (
            poi_html.xpath('.//*[contains(text(), "Address:")]/text()')[0]
            .strip()
            .split("Address: ")[-1]
        )
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        city = addr.city
        state = addr.state
        zip_code = addr.postcode
        phone = poi_html.xpath(".//p/text()")[1].split("Phone: ")[-1].strip()
        if not phone:
            phone = poi_html.xpath('.//span[contains(text(), "Phone:")]/text()')[
                0
            ].split(": ")[-1]
        hoo = poi_html.xpath('.//p[@class="p01 hours-text"]/text()')
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo).replace("â\x80\x93", "-") if hoo else ""

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code="",
            store_number="",
            phone=phone,
            location_type="",
            latitude="",
            longitude="",
            hours_of_operation=hours_of_operation,
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
