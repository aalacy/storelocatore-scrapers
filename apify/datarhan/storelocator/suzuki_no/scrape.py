import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://suzuki.no/forhandlere/"
    domain = "suzuki.no"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    data = (
        dom.xpath('//script[contains(text(), "parsedDealers = ")]/text()')[0]
        .split(";\n\n        allDealers")[0]
        .split("sedDealers =")[-1]
    )

    all_locations = json.loads(data)
    for poi in all_locations:
        hoo = []
        for day, hours in poi["hoursSales"].items():
            if not hours:
                hours = "closed"
            hoo.append(f"{day}: {hours}")
        hoo = ", ".join(hoo)
        if poi["name"] == "Test dealer":
            continue
        country_code = poi["country"]
        if country_code in ["Sverige", "Danmark", "Polen"]:
            continue

        item = SgRecord(
            locator_domain=domain,
            page_url="https://suzuki.no/forhandlere/",
            location_name=poi["name"],
            street_address=poi["address"],
            city=poi["city"],
            state="",
            zip_postal=poi["postalcode"],
            country_code=country_code,
            store_number=poi["orgnumber"],
            phone=poi["telephone"],
            location_type="",
            latitude=poi["lat"],
            longitude=poi["long"],
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
