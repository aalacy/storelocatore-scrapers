import re
import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://suzuki.ua/dealer"
    domain = "suzuki.ua"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    data = dom.xpath('//script[contains(text(), "allDealers")]/text()')[0]
    all_locations = re.findall(r"allDealers =(.+\]);", data)[0]
    all_locations = json.loads(all_locations)

    for poi in all_locations:
        geo = poi[0].split(", ")
        phone = (
            poi[5]
            .split("<br>")[0]
            .replace("Vodafone ", "")
            .split(",")[0]
            .split(":")[-1]
            .strip()
        )

        item = SgRecord(
            locator_domain=domain,
            page_url="https://suzuki.ua/car/1/vitara#/buyers/dealers",
            location_name=poi[-4].strip(),
            street_address=poi[1],
            city=poi[-1],
            state="",
            zip_postal="",
            country_code="UA",
            store_number="",
            phone=phone,
            location_type="",
            latitude=geo[0],
            longitude=geo[1],
            hours_of_operation="",
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
