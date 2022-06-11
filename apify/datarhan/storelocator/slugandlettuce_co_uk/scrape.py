import re
import demjson
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "slugandlettuce.co.uk"
    start_url = "https://www.slugandlettuce.co.uk/find-a-bar"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//div[@class="sites-by-region"]//a/@href')
    all_locations = [elem for elem in all_locations if elem != "#"]

    for url in all_locations:
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//h1[@class="section-heading"]/text()')
        location_name = location_name[-1] if location_name else "<MISSING>"
        address_raw = loc_dom.xpath('//ul[@class="menu vertical address"]/li/text()')
        address_raw = [elem.strip() for elem in address_raw if elem.strip()]
        if not address_raw:
            continue
        addr = parse_address_intl(" ".join(address_raw))
        street_address = address_raw[0]
        city = addr.city
        state = addr.state
        zip_code = addr.postcode
        country_code = addr.country
        phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')
        phone = phone[0] if phone else ""
        latitude = re.findall(r"lat: (.+?),", loc_response.text)
        latitude = latitude[0] if latitude else ""
        longitude = re.findall(r"lng: (.+?) }", loc_response.text)
        longitude = longitude[-1].strip() if longitude else ""
        hoo = loc_dom.xpath(
            '//h2[contains(text(), "Opening Times")]/following-sibling::div//text()'
        )
        hoo = [elem.strip() for elem in hoo if elem.strip()]
        hours_of_operation = " ".join(hoo) if hoo else ""

        loc_response = session.get(store_url + "/contact")
        geo = re.findall(r"(\{ lng: .+? \})", loc_response.text)[0]
        geo = demjson.decode(geo)

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
            latitude=geo["lat"],
            longitude=geo["lng"],
            hours_of_operation=hours_of_operation,
            raw_address=" ".join(address_raw),
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
