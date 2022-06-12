from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()
    start_url = "https://presscoffee.com/pages/location"
    domain = "presscoffee.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="iwt-content__content" and h4]')
    for poi_html in all_locations:
        if poi_html.xpath('.//p[contains(text(), "Coming Soon")]'):
            continue

        page_url = poi_html.xpath('.//a[@class="btn--main"]/@href')[0]
        page_url = urljoin(start_url, page_url)
        location_name = poi_html.xpath(".//h1/text()")[0].strip()
        raw_address = poi_html.xpath(".//h1/following-sibling::a[1]/text()")[-1].strip()
        if raw_address == "SEE MORE":
            raw_address = poi_html.xpath(
                './/div[@class="iwt-content__content-address"]//text()'
            )[-1].strip()
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        city = addr.city
        state = addr.state
        zip_code = addr.postcode
        phone = poi_html.xpath('.//a[contains(@href, "tel")]/text()')
        if not phone:
            phone = poi_html.xpath(
                './/div[@class="iwt-content__content-number"]/text()'
            )
        phone = phone[-1].strip() if phone else ""
        hoo = poi_html.xpath('.//div[@class="iwt-content__content-time"]//text()')
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo).replace(" (Temporary)", "") if hoo else ""

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
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
