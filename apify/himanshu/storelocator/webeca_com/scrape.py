import json
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.webeca.com/locations"
    domain = "webeca.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//script[@id="__NEXT_DATA__"]/text()')[0]
    all_locations = json.loads(all_locations)

    for poi in all_locations["props"]["pageProps"]["locations"]:
        page_url = urljoin(start_url, poi["slug"])
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        street_address = poi["address1"]
        if poi["address2"]:
            street_address += " " + poi["address2"]
        if poi["address3"]:
            street_address += " " + poi["address3"]
        hoo = loc_dom.xpath(
            '//h2[contains(text(), "Hours of Operation")]/following-sibling::div[1]//text()'
        )
        hoo = " ".join(hoo).split("Open two")[0].strip()

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["name"],
            street_address=street_address,
            city=poi["city"],
            state=poi["state"],
            zip_postal=poi["zipCode"],
            country_code="",
            store_number="",
            phone=poi["phoneNumber"],
            location_type="",
            latitude=poi["map"]["lat"],
            longitude=poi["map"]["lon"],
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
