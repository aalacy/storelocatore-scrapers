import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "usautoforce.com"
    start_url = "http://www.usautoforce.com/about/locations/"
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36"
    }
    response = session.get(start_url, headers=headers)
    dom = etree.HTML(response.text)

    data = dom.xpath('//script[contains(text(), "locations")]/text()')[-1].split(
        "var locations ="
    )[-1][:-1]
    all_locations = json.loads(data)
    for poi in all_locations:
        store_url = "http://www.usautoforce.com/about/locations/"
        if poi["tires_warehouse"]:
            location_type = "tires warehouse"
        elif poi["treadmaxx"]:
            location_type = "treadmaxx"
        else:
            location_type = "maxfinkelstein"

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=poi["title"].replace("&#8211;", "-"),
            street_address=poi["street"],
            city=poi["city"],
            state=poi["state"],
            zip_postal=poi["zip"],
            country_code="",
            store_number="",
            phone="",
            location_type=location_type,
            latitude=poi["lat"],
            longitude=poi["lng"],
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
