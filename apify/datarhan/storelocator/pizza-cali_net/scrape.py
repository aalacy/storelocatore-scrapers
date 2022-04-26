# -*- coding: utf-8 -*-
import re
import demjson
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

    start_url = "https://www.pizza-cali.net/area.php"
    domain = "pizza-cali.net"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//h3[@class="shop-name"]/a/@href')
    for url in all_locations:
        page_url = urljoin(start_url, url)
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)
        raw_address = loc_dom.xpath('//div[@id="shop-map-address"]/text()')
        raw_address = " ".join([e.strip() for e in raw_address if e.strip()])
        location_name = loc_dom.xpath('//section[@id="header-shop-info"]/h2/text()')[0]
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        phone = loc_dom.xpath('//div[@class="shop-tel"]/text()')[0].split("(")[0]
        geo = re.findall("myLatLng = (.+?);", loc_response.text)
        latitude = ""
        longitude = ""
        if geo:
            geo = demjson.decode(geo[0])
            latitude = geo["lat"]
            longitude = geo["lng"]
        hoo = " ".join(
            loc_dom.xpath('//div[@class="shop-time"]/text()')[0].split()
        ).replace("ご注文受付時間:", "")

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=addr.city,
            state=addr.state,
            zip_postal=addr.postcode,
            country_code=addr.country,
            store_number=page_url.split("=")[-1],
            phone=phone,
            location_type="",
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
