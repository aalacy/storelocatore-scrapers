# -*- coding: utf-8 -*-
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://www.thefoodwarehouse.com/assets/foodwarehouse/ajax/"
    domain = "thefoodwarehouse.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    all_locations = session.get(start_url, headers=hdr).json()
    for poi in all_locations:
        if "Coming Soon" in poi["name"]:
            continue
        raw_address = etree.HTML(poi["address"].replace("<br>", ", ")).xpath("//text()")
        raw_address = (
            " ".join([e.strip() for e in raw_address if e.strip()])
            .replace("\t", " ")
            .replace("\n", " ")
        )
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if street_address and addr.street_address_2:
            street_address += ", " + addr.street_address_2
        else:
            street_address = addr.street_address_2
        if not street_address:
            street_address = raw_address.split(", ")[0]
            if "unit" in street_address.lower():
                street_address += ", " + raw_address.split(", ")[1]
        street_address = street_address.replace(",,", ",")
        if street_address.endswith(","):
            street_address = street_address[:-1]
        hoo = etree.HTML(poi["opening-times"].replace("\n", ", ")).xpath("//text()")
        hoo = " ".join([e.strip() for e in hoo if e.strip()])

        item = SgRecord(
            locator_domain=domain,
            page_url=f'https://www.thefoodwarehouse.com{poi["url"]}',
            location_name=poi["name"],
            street_address=street_address,
            city=addr.city,
            state=addr.state,
            zip_postal=addr.postcode,
            country_code=addr.country,
            store_number=poi["storeNo"],
            phone=poi.get("store-number"),
            location_type="",
            latitude=poi["lat"],
            longitude=poi["lng"],
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
