import re
import json
from lxml import etree
from w3lib.html import remove_tags

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "specsonline.com"
    start_url = "https://specsonline.com/locations/"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath(
        '//div[@class="instore-store "]//a[contains(text(), "location detail")]/@href'
    )
    all_locations += dom.xpath(
        '//div[@class="instore-store hidden-stores"]//a[contains(text(), "location detail")]/@href'
    )

    data = dom.xpath('//script[@id="maplistko-js-extra"]/text()')[0]
    data = re.findall("ParamsKo =(.+);", data)[0]
    data = json.loads(data)

    for poi in data["KOObject"][0]["locations"]:
        page_url = poi["locationUrl"]
        location_name = poi["title"]
        if "Coming soon" in location_name:
            continue
        address_raw = etree.HTML(poi["address"])
        address_raw = address_raw.xpath(".//text()")
        address_raw = [elem.strip() for elem in address_raw if elem.strip()]
        if len(address_raw) == 3:
            address_raw = [", ".join(address_raw[:2])] + address_raw[2:]
        street_address = address_raw[0]
        city = address_raw[1].split(",")[0]
        state = address_raw[1].split(",")[-1].split()[0]
        if state.isdigit():
            state = "<MISSING>"
        zip_code = address_raw[1].split(",")[-1].split()[-1]
        phone = ""
        if poi.get("simpledescription"):
            phone = remove_tags(poi["simpledescription"]).split()[0]
        latitude = poi["latitude"]
        longitude = poi["longitude"]

        loc_response = session.get(page_url, headers=hdr)
        loc_dom = etree.HTML(loc_response.text)
        hours_of_operation = loc_dom.xpath('//p[@class="maplist-hours"]/text()')
        hours_of_operation = hours_of_operation[0].strip() if hours_of_operation else ""

        if phone == "<MISSING>":
            phone = loc_dom.xpath('//span[@itemprop="telephone"]/text()')
            phone = phone[0] if phone else ""

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
