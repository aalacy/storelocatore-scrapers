import re
import json
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests(verify_ssl=False)
    domain = "bostons.com"
    start_url = "https://www.bostons.com/locations/index.html?location=all"

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_stores = dom.xpath('//a[@itemprop="url"]/@href')
    for url in all_stores:
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        c_soon = loc_dom.xpath('//img[@alt="Banner image saying Coming Soon."]')
        if c_soon:
            continue
        data = loc_dom.xpath('//script[contains(text(), "var data =")]/text()')[0]
        data = re.findall("var data = (.+?) var", data.replace("\n", ""))[0]
        data = json.loads(data)

        location_name = data["name"]
        street_address = data["address"]["streetAddress"]
        city = data["address"]["addressLocality"]
        city = city if city else "<MISSING>"
        state = data["address"]["addressRegion"]
        phone = data["telephone"]
        location_type = data["@type"]
        latitude = data["geo"]["latitude"]
        longitude = data["geo"]["longitude"]
        hoo = loc_dom.xpath('//div[@class="location__meta-hours-list"]/dl//text()')
        hoo = [elem.strip() for elem in hoo if elem.strip]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal="",
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
