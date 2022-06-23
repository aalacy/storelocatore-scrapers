import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://eu.christianlouboutin.com/fr_fr/storelocator/"
    domain = "christianlouboutin.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    data = (
        dom.xpath('//script[contains(text(), "LocatorData   =")]/text()')[0]
        .split("LocatorData   =")[1]
        .split(";\n    window")[0]
    )
    data = json.loads(data)

    for poi in data["retailers"]:
        hoo = []
        for e in poi["schedule_data"]:
            hoo.append(f'{e["day"]}: {e["label"]}')
        hoo = ", ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url=poi["store_url"],
            location_name=poi["name"],
            street_address=poi["street"],
            city=poi["city"],
            state="",
            zip_postal=poi["zipcode"],
            country_code=poi["country"],
            store_number=poi["retailer_id"],
            phone=poi["phone"],
            location_type="",
            latitude=poi["latitude"],
            longitude=poi["longitude"],
            hours_of_operation=hoo,
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
