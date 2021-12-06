from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


def fetch_data():
    session = SgRequests()

    start_url = "https://www.gnc.ca/on/demandware.store/Sites-GNCCA-Site/en_CA/Stores-FindStores"
    domain = "gnc.ca"
    hdr = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:94.0) Gecko/20100101 Firefox/94.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,ru-RU;q=0.8,ru;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/x-www-form-urlencoded",
        "DNT": "1",
    }
    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.CANADA],
        expected_search_radius_miles=100,
    )
    for code in all_codes:
        frm = {
            "dwfrm_storelocator_countryCode": "CA",
            "dwfrm_storelocator_distanceUnit": "km",
            "dwfrm_storelocator_postalCode": code[:3],
            "dwfrm_storelocator_maxdistance": "100",
            "dwfrm_storelocator_findbyzip": "Search",
        }
        response = session.post(start_url, headers=hdr, data=frm)
        dom = etree.HTML(response.text)
        all_locations = dom.xpath('//a[@title="View Store Details"]/@href')
        for page_url in all_locations:
            page_url = urljoin(start_url, page_url)
            loc_response = session.get(page_url)
            loc_dom = etree.HTML(loc_response.text)

            location_name = loc_dom.xpath('//h1[@itemprop="name"]/text()')[0]
            street_address = loc_dom.xpath('//span[@itemprop="streetAddress"]//text()')
            street_address = " ".join([e.strip() for e in street_address if e.strip()])
            city = loc_dom.xpath('//span[@itemprop="addressLocality"]/text()')[0]
            state = loc_dom.xpath('//span[@itemprop="addressRegion"]/text()')[0]
            zip_code = loc_dom.xpath('//span[@itemprop="postalCode"]//text()')[0]
            phone = loc_dom.xpath('//a[@class="store-phone"]/text()')[0]
            store_number = loc_dom.xpath('//span[@class="store-id"]/text()')[0].split(
                "#"
            )[-1]
            latitude = loc_dom.xpath('//meta[@itemprop="latitude"]/@content')[0]
            longitude = loc_dom.xpath('//meta[@itemprop="longitude"]/@content')[0]
            hoo = loc_dom.xpath('//meta[@itemprop="openingHours"]/@content')
            hoo = " ".join(hoo)

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code="CA",
                store_number=store_number,
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
