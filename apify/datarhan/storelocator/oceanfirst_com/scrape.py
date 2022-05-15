import re
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "oceanfirst.com"
    start_url = "https://oceanfirst.com/locations/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_states = dom.xpath('//ul[@class="state-list"]/li/a/@href')
    all_states = [e.strip() for e in all_states if e.strip()]
    for url in all_states:
        response = session.get(urljoin(start_url, url))
        dom = etree.HTML(response.text)
        locations = dom.xpath(
            '//div[@class="branch-list-item"]/p[@class="actions"]/a/@href'
        )
        all_locations = [e for e in locations if "/maps/" not in e]
        for url in all_locations:
            page_url = urljoin(start_url, url)
            loc_response = session.get(page_url)
            loc_dom = etree.HTML(loc_response.text)

            location_name = loc_dom.xpath('//h1[@class="title"]/text()')
            location_name = location_name[0] if location_name else ""
            raw_address = loc_dom.xpath('//div[@class="branch-address"]/text()')
            raw_address = [elem.strip() for elem in raw_address if elem.strip()]
            if not raw_address:
                continue
            location_type = ""
            if "Temporarily Closed" in raw_address[0]:
                raw_address = raw_address[1:]
                location_type = "Temporarily Closed"
            street_address = raw_address[0]
            city = raw_address[-1].split(", ")[0]
            state = raw_address[-1].split(", ")[-1].split()[0]
            zip_code = raw_address[-1].split(", ")[-1].split()[-1]
            phone = loc_dom.xpath('//span[@class="phone"]/text()')
            phone = phone[0] if phone else ""
            geo = re.findall(r"LatLng\((.+)\)", loc_response.text)[0].split(", ")
            latitude = geo[0]
            longitude = geo[1]
            hoo = loc_dom.xpath('//div[@class="branch_hours_days clearfix"]//text()')
            hoo = " ".join(hoo).split("January")[0].strip() if hoo else ""
            hours_of_operation = hoo.strip() if hoo and hoo.strip() else ""

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
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
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
