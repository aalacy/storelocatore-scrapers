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
    domain = "cesco.com"
    start_url = "https://www.crescentelectric.com/locations-map"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    }

    response = session.get(start_url, headers=headers)
    dom = etree.HTML(response.text)
    data = (
        dom.xpath('//script[contains(text(), "serverSideModel")]/text()')[0]
        .split("serverSideModel =")[-1]
        .strip()[:-1]
    )
    data = demjson.decode(data)

    for poi in data["branches"]:
        street_address = poi["infoWindowData"]["addressLine1"]
        if poi["infoWindowData"]["addressLine2"]:
            street_address += ", " + poi["infoWindowData"]["addressLine2"]
        page_url = urljoin(start_url, poi["infoWindowData"]["storePageUrl"])
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)
        hoo = loc_dom.xpath('//div[@class="store__hours"]/div//text()')
        hoo = " ".join([e.strip() for e in hoo if e.strip()])

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["infoWindowData"]["name"],
            street_address=street_address,
            city=poi["infoWindowData"]["city"],
            state=poi["infoWindowData"]["state"],
            zip_postal=poi["infoWindowData"]["zipCode"],
            country_code="",
            store_number=poi["storeNumber"],
            phone=poi["infoWindowData"]["phoneNumber"],
            location_type=poi["locationType"],
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
