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
    start_url = "https://paniqescaperoom.com/"
    domain = "paniqescaperoom.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//a[@data-region="us"]/@href')
    for url in all_locations:
        page_url = urljoin(start_url, url)
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        poi = loc_dom.xpath('//script[contains(text(), "GeoCoordinates")]/text()')
        if loc_dom.xpath('//div[contains(text(), "Coming Soon!")]'):
            continue
        if not poi:
            continue
        if loc_dom.xpath('//div[contains(text(), "OPENING SOON")]'):
            continue
        if loc_dom.xpath('//div[contains(text(), "PERMANENTLY CLOSED")]'):
            continue
        if loc_dom.xpath('//div[contains(text(), "Permanently closed")]'):
            continue

        hoo = loc_dom.xpath(
            '//h4[contains(text(), "Opening Hours")]/following-sibling::div[@class="table-wrap"][1]//text()'
        )
        hoo = " ".join([e.strip() for e in hoo if e.strip()])
        all_locations = [json.loads(poi[0])]
        if not all_locations[0].get("address"):
            all_locations = all_locations[0].get("subOrganization")
        if all_locations:
            for poi in all_locations:
                location_type = poi["@type"]
                if loc_dom.xpath('//div[contains(text(), "temporarily closed")]'):
                    location_type = "temporarily closed"

                item = SgRecord(
                    locator_domain=domain,
                    page_url=page_url,
                    location_name=poi["name"],
                    street_address=poi["address"]["streetAddress"],
                    city=poi["address"]["addressLocality"],
                    state=poi["address"]["addressRegion"],
                    zip_postal=poi["address"]["postalCode"],
                    country_code=poi["address"]["addressCountry"],
                    store_number="",
                    phone=poi["telephone"],
                    location_type=location_type,
                    latitude=poi["geo"]["latitude"],
                    longitude=poi["geo"]["longitude"],
                    hours_of_operation=hoo,
                )

                yield item
        else:
            location_name = loc_dom.xpath("//h1/text()")[0].strip()
            raw_address = loc_dom.xpath('//a[contains(@href, "maps")]/span/text()')[0]
            street_address = raw_address.split(location_name)[0]
            phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')[0]
            poi = loc_dom.xpath('//script[contains(text(), "GeoCoordinates")]/text()')[
                0
            ]
            poi = json.loads(poi)

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=location_name,
                state=raw_address.split(",")[1].split()[0],
                zip_postal=raw_address.split(",")[1].split()[1],
                country_code="USA",
                store_number="",
                phone=phone,
                location_type=poi["@type"],
                latitude=poi["geo"]["latitude"],
                longitude=poi["geo"]["longitude"],
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
