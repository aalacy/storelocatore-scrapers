import re
import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()
    start_url = "https://heidisbrooklyndeli.com/locations/"
    domain = "heidisbrooklyndeli.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="list-item-location"]')
    for poi_html in all_locations:
        page_url = poi_html.xpath('.//a[@id="get-derections"]/@href')
        if not page_url:
            continue
        page_url = page_url[0]

        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)
        data = loc_dom.xpath(
            '//script[contains(text(), "aplistFrontScriptParams")]/text()'
        )[0]
        data = re.findall("Params =(.+);", data)[0]
        data = json.loads(data)
        poi = json.loads(data["location"])

        location_name = poi_html.xpath(".//h2/text()")
        location_name = location_name[0] if location_name else ""
        raw_data = loc_dom.xpath('//div[@class="address-left"]/text()')
        if not raw_data:
            raw_data = loc_dom.xpath('//div[@id="MapDescription"]/p[3]/text()')
        raw_data = [e.strip() for e in raw_data if e.strip()]
        addr = parse_address_intl(" ".join(raw_data))
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        city = addr.city
        state = addr.state
        zip_code = addr.postcode
        country_code = addr.country
        phone = poi_html.xpath(".//span/text()")[-1].split(":")[-1].strip()
        if not phone:
            continue
        latitude = poi["latitude"]
        longitude = poi["longitude"]
        hoo = loc_dom.xpath('//div[@class="time-table"]//div//text()')
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo) if hoo else ""

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
            store_number="",
            phone=phone,
            location_type="",
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=" ".join(raw_data)
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
