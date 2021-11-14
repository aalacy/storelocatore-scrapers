from lxml import etree

from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://www.congebec.com/index.php/en/locations/"
    domain = "congebec.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="organic-column one-half" and h4]')
    for poi_html in all_locations:
        store_url = start_url
        location_name = poi_html.xpath(".//h4/text()")[0]
        raw_address = (
            poi_html.xpath(".//p/text()")[0]
            .replace("Adress: ", "")
            .replace("\xa0", " ")
            .replace("Address: ", "")
        )
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        city = addr.city
        state = addr.state
        zip_code = addr.postcode
        country_code = addr.country
        raw_data = poi_html.xpath('.//p[contains(text(), "Adress")]/text()')
        if not raw_data:
            raw_data = poi_html.xpath('.//p[contains(text(), "Address")]/text()')
        phone = poi_html.xpath('.//strong[contains(text(), "Phone")]/following::text()')
        phone = phone[0].replace(":", "").strip() if phone else ""
        hoo = poi_html.xpath(
            './/strong[contains(text(), "Opening hours")]/following::text()'
        )
        hoo = hoo[0].strip()[1:] if hoo else ""

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
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
