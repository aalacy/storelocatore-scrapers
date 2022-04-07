# -*- coding: utf-8 -*-
import re
import yaml
from yaml import FullLoader
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "http://restaurants-delifrance.com/store-locator/"
    domain = "restaurants-delifrance.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    all_locations = re.findall(r"Marker\((.+?)\);", response.text.replace("\n", ""))
    for e in all_locations:
        poi = yaml.load(
            e.replace("new google.maps.LatLng(", '"').replace("),", '",'),
            Loader=FullLoader,
        )
        page_url = poi["site"]
        loc_response = session.get(page_url)
        if loc_response.status_code != 200:
            continue
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//div[@class="pad-10c"]/span/text()')[0]
        raw_address = loc_dom.xpath('//div[@class="locator-adrss"]//text()')
        raw_address = " ".join([e.strip() for e in raw_address if e.strip()])
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=addr.city,
            state=addr.state,
            zip_postal=addr.postcode,
            country_code=addr.country,
            store_number="",
            phone="",
            location_type="",
            latitude=poi["position"].split(", ")[0],
            longitude=poi["position"].split(", ")[1],
            hours_of_operation="",
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
