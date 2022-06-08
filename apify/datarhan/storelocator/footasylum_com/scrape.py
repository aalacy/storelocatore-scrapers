# -*- coding: utf-8 -*-
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

    start_url = (
        "https://support.footasylum.co.uk/api/nuqlium/data/prod/index.php?v=5yf9hd"
    )
    domain = "footasylum.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    frm = {
        "DataIndex": "100029",
        "output": "json",
        "pagetype": "pages",
        "pagekey": "store-finder-page",
        "settings[pricelist]": "retail_gbp",
        "settings[mode]": "web",
    }
    data = session.post(start_url, data=frm, headers=hdr).json()
    for poi in data["data"]["content"]["content"][0]["data"]["block_reference"]:
        page_url = urljoin("https://www.footasylum.com/store-locator/", poi["url"])
        raw_adddress = etree.HTML(poi["address"]).xpath("//text()")
        raw_adddress = ", ".join([e.strip() for e in raw_adddress if e.strip()])
        addr = parse_address_intl(raw_adddress)
        street_address = addr.street_address_1
        if street_address and addr.street_address_2:
            street_address += " " + addr.street_address_2
        else:
            street_address = addr.street_address_2
        hoo = etree.HTML(poi["opening_times"]).xpath("//text()")
        hoo = " ".join([e.strip() for e in hoo if e.strip()])
        poi_html = etree.HTML(poi["_html"])
        phone = poi_html.xpath('//a[@class="store-telephone"]/div/text()')

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["name"],
            street_address=street_address,
            city=addr.city,
            state=addr.state,
            zip_postal=addr.postcode,
            country_code="",
            store_number=poi["store_id"],
            phone=phone,
            location_type="",
            latitude=poi["latitude"],
            longitude=poi["longitude"],
            hours_of_operation=hoo,
            raw_address=raw_adddress,
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
