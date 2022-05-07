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
    start_url = "https://cars.suzuki.ie/find-a-dealer/"
    domain = "suzuki.ie"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    data = (
        dom.xpath('//script[contains(text(), "allDealers")]/text()')[0]
        .split("allDealers =")[-1]
        .split(";\r\n        var")[0]
    )

    all_locations = json.loads(data)
    for poi in all_locations:
        raw_address = poi["address"]
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += ", " + addr.street_address_2
        hoo = []
        if poi["openingHours"]:
            for e in poi["openingHours"]:
                hoo.append(f'{e["day"]}: {e["times"]}')
        hoo = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url=poi["visitDealerPageLink"],
            location_name=poi["name"],
            street_address=street_address,
            city=addr.city,
            state="",
            zip_postal=poi["postcode"],
            country_code="IE",
            store_number=poi["dealerCode"],
            phone=poi["phone"],
            location_type=poi["site"],
            latitude=poi["location"]["lat"],
            longitude=poi["location"]["lng"],
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
