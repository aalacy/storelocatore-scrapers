import demjson
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://brooklynbedding.com/pages/casa-grande"
    domain = "brooklynbedding.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    data = (
        dom.xpath('//script[contains(text(), "showrooms")]/text()')[0]
        .split("showrooms =")[1]
        .strip()
    )
    data = demjson.decode(data)
    for poi in data["blocks"]:
        page_url = urljoin(start_url, poi["page"])
        hoo = f'MONDAY - FRIDAY: {poi["mfHours"]}, SATURDAY: {poi["satHours"]}, SUNDAY: {poi["sunHours"]}'

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["title"].replace("&amp;", "&"),
            street_address=poi["streetAddress"],
            city=poi["city"],
            state=poi["state"],
            zip_postal=poi["zip"],
            country_code="",
            store_number="",
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
