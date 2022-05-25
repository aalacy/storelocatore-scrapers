import re
import json
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
    start_url = "https://paniqescaperoom.com/"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//a[@data-region="us"]/@href')
    for url in all_locations:
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        if loc_dom.xpath('//div[contains(text(), "Coming Soon!")]'):
            continue
        poi = loc_dom.xpath('//script[contains(text(), "GeoCoordinates")]/text()')
        if not poi:
            continue
        poi = json.loads(poi[0])
        if loc_dom.xpath('//div[contains(text(), "OPENING SOON")]'):
            continue
        if loc_dom.xpath('//div[contains(text(), "PERMANENTLY CLOSED")]'):
            continue
        if loc_dom.xpath('//div[contains(text(), "Permanently closed")]'):
            continue

        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        raw_address = ""
        if not poi.get("address"):
            raw_address = (
                loc_dom.xpath('//a[contains(@href, "maps")]/@href')[0]
                .split("query=")[-1]
                .split("&query")[0]
                .replace("+", " ")
                .replace("%2C", ",")
            )
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            street_address = street_address if street_address else "<MISSING>"
            city = addr.city
            state = addr.state
            zip_code = addr.postcode
            country_code = "<MISSING>"
        else:
            street_address = poi["address"]["streetAddress"]
            street_address = street_address if street_address else "<MISSING>"
            city = poi["address"]["addressLocality"]
            city = city if city else "<MISSING>"
            state = poi["address"]["addressRegion"]
            state = state if state else "<MISSING>"
            zip_code = poi["address"]["postalCode"]
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = poi["address"]["addressCountry"]
            country_code = country_code if country_code else "<MISSING>"
        if poi.get("telephone"):
            phone = poi["telephone"]
        else:
            phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')
            phone = phone[0] if phone else "<MISSING>"
        location_type = poi["@type"]
        latitude = poi["geo"]["latitude"]
        longitude = poi["geo"]["longitude"]
        hoo = loc_dom.xpath(
            '//h4[contains(text(), "Opening Hours")]/following-sibling::div[@class="table-wrap"][1]//text()'
        )
        hoo = " ".join([e.strip() for e in hoo if e.strip()])
        if loc_dom.xpath('//div[contains(text(), "temporarily closed")]'):
            location_type = "temporarily closed"

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code="US",
            store_number="",
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hoo,
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
