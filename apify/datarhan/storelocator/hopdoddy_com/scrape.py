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
    domain = "hopdoddy.com"
    start_url = "https://www.hopdoddy.com/locations"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath(
        '//a[@class="alllocations__buttondetails w-inline-block"]/@href'
    )

    for url in all_locations:
        page_url = urljoin(start_url, url)
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)
        poi = loc_dom.xpath('//script[@type="application/ld+json"]/text()')[0]
        poi = json.loads(poi)
        location_name = loc_dom.xpath("//h1/text()")[0]
        store_number = loc_dom.xpath("//@data-location-olo-id")[0]
        geo = loc_dom.xpath('//iframe[contains(@src, "maps")]/@src')
        latitude = ""
        longitude = ""
        if geo:
            geo = geo[0].split("1d")[-1].split("!3")[0].split("!2d")
            latitude = geo[0]
            longitude = geo[1]

        hours_of_operation = []
        hoo_response = session.get(
            "https://na6c0i4fb0.execute-api.us-west-2.amazonaws.com/calendars/{}".format(
                store_number
            )
        )
        hoo = json.loads(hoo_response.text)
        for elem in hoo["data"]:
            hours_of_operation.append(f'{elem["day"]} {elem["opens"]} {elem["closes"]}')
        hoo = " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=poi["address"]["streetAddress"],
            city=poi["address"]["addressLocality"],
            state=poi["address"]["addressRegion"],
            zip_postal=poi["address"]["postalCode"],
            country_code=poi["address"]["addressCountry"],
            store_number=store_number,
            phone=poi["telephone"],
            location_type=poi["@type"],
            latitude=latitude,
            longitude=longitude,
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
