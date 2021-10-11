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
    session = SgRequests().requests_retry_session(retries=1, backoff_factor=0.3)

    domain = "spherion.com"
    start_url = "https://www.spherion.com/our-offices/"
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    }

    response = session.get(start_url, headers=headers)
    dom = etree.HTML(response.text)

    data = dom.xpath('//script[contains(text(), "searchResults")]/text()')[0]
    data = re.findall("ROUTE_DATA__ =(.+)", data)[0]
    data = json.loads(data)

    all_locations = data["searchResults"]["hits"]["hits"]
    next_page = dom.xpath('//a[@rel="next"]/@href')
    while next_page:
        response = session.get(urljoin(start_url, next_page[0]), headers=headers)
        dom = etree.HTML(response.text)

        data = dom.xpath('//script[contains(text(), "searchResults")]/text()')[0]
        data = re.findall("ROUTE_DATA__ =(.+)", data)[0]
        data = json.loads(data)

        all_locations += data["searchResults"]["hits"]["hits"]
        next_page = dom.xpath('//a[@rel="next"]/@href')

    for poi in all_locations:
        store_url = urljoin(start_url, poi["_source"]["url"][0])
        if "applyohio.com" in store_url:
            continue
        loc_response = session.get(store_url, headers=headers)
        loc_dom = etree.HTML(loc_response.text)

        location_name = poi["_source"]["title_office"]
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = poi["_source"]["address_line1"][0]
        if poi["_source"]["address_line2"]:
            street_address += ", " + poi["_source"]["address_line2"][0]
        street_address = street_address.strip()
        if "virtual office" in street_address:
            continue
        if street_address.endswith(","):
            street_address = street_address[:-1]
        city = poi["_source"]["locality_1"]
        city = city[0] if city else "<MISSING>"
        state = poi["_source"]["administrative_area"]
        state = state[0].upper() if state else "<MISSING>"
        zip_code = poi["_source"]["postal_code"][0]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = poi["_source"].get("field_phone")
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        if "office is closed" in street_address:
            street_address = "<MISSING>"
            location_type = "closed"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if poi["_source"].get("lat_lon"):
            latitude = poi["_source"]["lat_lon"][0].split(",")[0]
            longitude = poi["_source"]["lat_lon"][0].split(",")[-1]
        hours_of_operation = loc_dom.xpath(
            '//*[contains(@class, "time-table__item")]/span/text()'
        )
        hours_of_operation = (
            " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
        )

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
            store_number=store_number,
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
