import re
import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://www.suzukinajeebauto.com/en/locate-our-branches/show-rooms"
    domain = "suzukinajeebauto.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    data = dom.xpath('//script[contains(text(), "locations =")]/text()')[0]
    data = re.findall("locations =(.+?;)", data.replace("\n", ""))[2][:-1]
    all_locations = json.loads(data)
    for poi in all_locations:
        raw_address = poi["Contents"]["Address"]["Content"]
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += ", " + addr.street_address_2
        hoo = etree.HTML(poi["Contents"]["Working Days"]["Content"]).xpath("//text()")
        hoo = " ".join([e.strip() for e in hoo if e.strip()])

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=poi["Name"],
            street_address=street_address,
            city=addr.city,
            state=addr.state,
            zip_postal=addr.postcode,
            country_code="Saudi Arabia",
            store_number="",
            phone=poi["Contents"]["Phone"]["Content"],
            location_type="",
            latitude=poi["Contents"]["x"]["Content"],
            longitude=poi["Contents"]["y"]["Content"],
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
