# -*- coding: utf-8 -*-
import re
import json
from lxml import etree

from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://www.newcold.com/sites/"
    domain = "newcold.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    data = dom.xpath("""//*[contains(text(), '"places":')]/text()""")[0]
    data = re.findall(r".maps\((.+)\).data", data)[0]
    data = json.loads(data)

    all_locations = data["places"]
    for poi in all_locations:
        store_url = etree.HTML(poi["content"]).xpath("//a/@href")[0]
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        raw_address = loc_dom.xpath('//p[strong[contains(text(), "Address")]]/text()')[
            :2
        ]
        if not raw_address:
            raw_address = loc_dom.xpath(
                '//header[h3[contains(text(), "Address")]]/following-sibling::div[1]/p/text()'
            )[:3]
        raw_address = [e.strip() for e in raw_address if "+" not in e]
        addr = parse_address_intl(" ".join(raw_address))

        location_name = poi["title"]
        street_address = poi["address"]
        city = poi["location"]["city"]
        state = poi["location"].get("state")
        if not state:
            state = addr.state
        zip_code = poi["location"].get("postal_code")
        if not zip_code:
            zip_code = addr.postcode
        country_code = poi["location"]["country"]
        if country_code == "Verenigde Staten":
            country_code = "United States"
        store_number = poi["id"]
        phone = loc_dom.xpath('//div[@class="iconbox_content_container "]/p/text()')
        phone = [e.strip() for e in phone if "+" in e]
        phone = phone[0].replace("\xa0", " ").strip() if phone else ""
        latitude = poi["location"]["lat"]
        longitude = poi["location"]["lng"]
        hoo = loc_dom.xpath('//div[@class="avia-animated-number-content"]/p/text()')
        hours_of_operation = (
            hoo[-1].split(":")[-1].strip().replace("Ouvrir ", "") if hoo else ""
        )

        if location_name == "NewCold Wakefield":
            zip_code = "WF3 4FE"

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
