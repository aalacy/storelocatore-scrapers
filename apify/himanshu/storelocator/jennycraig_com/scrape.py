# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://locations.jennycraig.com/"
    domain = "jennycraig.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_states = dom.xpath('//div[@class="map-list-item is-single"]/a/@href')
    for url in all_states:
        response = session.get(url)
        dom = etree.HTML(response.text)
        all_cities = dom.xpath('//div[@class="map-list-item is-single"]/a/@href')
        for url in all_cities:
            response = session.get(url)
            dom = etree.HTML(response.text)

            all_locations = dom.xpath('//div[@class="location-name mb-20"]/a/@href')
            for page_url in all_locations:
                loc_response = session.get(page_url)
                if str(loc_response.url) != page_url:
                    continue
                loc_dom = etree.HTML(loc_response.text)

                poi = loc_dom.xpath(
                    '//script[contains(text(), "streetAddress")]/text()'
                )[0]
                poi = json.loads(poi)[0]
                zip_code = poi["address"]["postalCode"]
                country_code = "US"
                if len(zip_code.split()) == 2:
                    country_code = "CA"
                hoo = loc_dom.xpath('//div[@class="hours"]//text()')
                hoo = " ".join([e.strip() for e in hoo if e.strip()])

                item = SgRecord(
                    locator_domain=domain,
                    page_url=page_url,
                    location_name=poi["name"],
                    street_address=poi["address"]["streetAddress"],
                    city=poi["address"]["addressLocality"],
                    state=poi["address"]["addressRegion"],
                    zip_postal=zip_code,
                    country_code=country_code,
                    store_number="",
                    phone=poi["address"]["telephone"],
                    location_type=poi["@type"],
                    latitude=poi.get("geo", {}).get("latitude"),
                    longitude=poi.get("geo", {}).get("longitude"),
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
