# -*- coding: utf-8 -*-
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


def fetch_data():
    session = SgRequests()

    start_url = "https://www.bonmarche.co.uk/on/demandware.store/Sites-BONMARCHE-GB-Site/en_GB/Stores-FindStores?lat={}&lng={}&dwfrm_storelocator_findbygeocoord=Search&format=ajax&amountStoresToRender=5&checkout=false"
    domain = "bonmarche.co.uk"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    all_coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.BRITAIN], expected_search_radius_miles=50
    )
    for lat, lng in all_coords:
        response = session.get(start_url.format(lat, lng), headers=hdr)
        dom = etree.HTML(response.text)

        all_locations = dom.xpath('//a[contains(text(), "Show store page")]/@href')
        for url in all_locations:
            page_url = urljoin(start_url, url)
            loc_response = session.get(page_url)
            loc_dom = etree.HTML(loc_response.text)

            location_name = loc_dom.xpath("//h1/text()")[0].replace("\n", " ").strip()
            street_address = loc_dom.xpath('//div[@itemprop="streetAddress"]/text()')[
                0
            ].strip()
            city = loc_dom.xpath('//div[@itemprop="addressLocality"]/text()')[0].strip()
            zip_code = loc_dom.xpath('//div[@itemprop="postalCode"]/text()')[0].strip()
            state = loc_dom.xpath('//div[@itemprop="addressRegion"]/text()')[0].strip()
            phone = loc_dom.xpath('//span[@itemprop="telephone"]/text()')[0].strip()
            latitude = loc_dom.xpath('//meta[@itemprop="latitude"]/@content')[0]
            longitude = loc_dom.xpath('//meta[@itemprop="longitude"]/@content')[0]
            hoo = loc_dom.xpath('//div[@class="storehours"]//text()')
            hoo = " ".join([e.strip() for e in hoo if e.strip()]).replace(
                "--", "closed"
            )

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code="UK",
                store_number="",
                phone=phone,
                location_type="",
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
