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

    start_url = "https://www.kaptest.com/study/"
    domain = "kaptest.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_courses = dom.xpath(
        '//h3[contains(text(), "Courses by Location")]/following-sibling::div[1]/p/a/@href'
    )
    for url in all_courses:
        response = session.get(url)
        dom = etree.HTML(response.text)
        all_states = dom.xpath('//div[@class="state_options"]/a/@href')
        for url in all_states:
            response = session.get(urljoin(start_url, url))
            dom = etree.HTML(response.text)
            all_cities = dom.xpath('//table[@id="city_list"]//a/@href')
            for url in all_cities:
                page_url = urljoin(start_url, url)
                response = session.get(page_url)
                dom = etree.HTML(response.text)
                all_locations = dom.xpath('//div[@id="hor_school_scroll"]/div')
                for poi_html in all_locations:
                    raw_data = poi_html.xpath(".//p/text()")
                    raw_data = [e.strip() for e in raw_data if e.strip()]
                    if len(raw_data) == 2:
                        raw_data = [""] + raw_data
                    phone = ""
                    if len(raw_data) == 4:
                        phone = raw_data[1]
                        raw_data = [raw_data[0]] + raw_data[2:]
                    if raw_data[0].split("-")[0].isdigit():
                        phone = raw_data[0]
                        raw_data = raw_data = [""] + raw_data[1:]
                    location_name = raw_data[0]
                    if not location_name:
                        location_name = "<MISSING>"
                    raw_address = ", ".join(raw_data[1:])
                    if not raw_address:
                        continue
                    addr = parse_address_intl(raw_address)
                    street_address = addr.street_address_1
                    if street_address and addr.street_address_2:
                        street_address += ", " + addr.street_address_2
                    else:
                        street_address = addr.street_address_2
                    if not street_address:
                        street_address = raw_address.split(", ")[0].split(" - ")[-1]

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
                        location_type="",
                        latitude="",
                        longitude="",
                        hours_of_operation="",
                        raw_address=raw_address,
                    )

                    yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.RAW_ADDRESS}),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
