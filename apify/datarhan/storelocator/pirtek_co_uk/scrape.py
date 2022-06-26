import re
import demjson
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "pirtek.co.uk"
    start_url = "https://www.pirtek.co.uk/find-service-centre/"

    response = session.get(start_url)
    all_locations = re.findall(r"addMarker\((.+?)\);", response.text)
    all_locations = [
        e.split(",")[-1].strip()[1:-1] for e in all_locations if "https" in e
    ]
    for page_url in all_locations:
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//h1[@class="post-details--info-title"]/text()')
        if not location_name:
            location_name = loc_dom.xpath('//h2[@class="vc_custom_heading"]/text()')
        location_name = location_name[0] if location_name else ""
        street_address = loc_dom.xpath('//div[@class="unit-number"]/text()')[0]
        street_address_2 = loc_dom.xpath('//div[@class="street"]/text()')
        if street_address_2:
            street_address += " " + street_address_2[0]
        city = loc_dom.xpath('//div[@class="city"]/text()')[0]
        state = loc_dom.xpath('//div[@class="county"]/text()')
        state = state[0] if state else ""
        zip_code = loc_dom.xpath('//div[@class="postcode"]/text()')
        zip_code = zip_code[0] if zip_code else ""
        phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')
        phone = phone[0] if phone else ""
        geo = re.findall(r"center: (\{.+?\}),", loc_response.text)[0]
        geo = demjson.decode(geo)
        latitude = geo["lat"]
        longitude = geo["lng"]
        hoo = loc_dom.xpath('//div[@class="open-hours-table"]//text()')
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo) if hoo else ""
        temp_closed = loc_dom.xpath('//p[contains(text(), "Temporarily closed.")]')
        location_type = "Temporarily closed" if temp_closed else ""

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
