import json
from lxml import etree

from sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://www.laura.ca/en/stores-list/?dwfrm_storelocator_countryCode=CANADA&dwfrm_storelocator_distanceUnit=kilometers&dwfrm_storelocator_maxdistance=200&dwfrm_storelocator_lat=&dwfrm_storelocator_long=&dwfrm_storelocator_mapZoom=&dwfrm_storelocator_mapCenter=&dwfrm_storelocator_mapBounds=&dwfrm_storelocator_location={}&dwfrm_storelocator_storeType=&dwfrm_storelocator_findbyzip=Search"
    domain = "laura.ca"
    scraped_items = []
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.CANADA], expected_search_radius_miles=100
    )
    for code in all_codes:
        response = session.get(start_url.format(code), headers=hdr)
        dom = etree.HTML(response.text)
        all_locations = dom.xpath("//tr[@data-store-details]")

        for poi_html in all_locations:
            poi = json.loads(poi_html.xpath("@data-store-details")[0])
            if poi["id"] in scraped_items:
                continue
            scraped_items.append(poi["id"])
            store_url = "https://www.laura.ca/en/store-details/?StoreID={}".format(
                poi["id"]
            )
            loc_response = session.get(store_url)
            loc_dom = etree.HTML(loc_response.text)

            location_name = poi["name"]
            raw_address = poi_html.xpath('.//div[@class="address-details"]/text()')
            raw_address = [e.strip() for e in raw_address if e.strip()]
            street_address = raw_address[0]
            city = raw_address[1].split(", ")[0]
            state = raw_address[1].split(", ")[-1].split()[0]
            zip_code = raw_address[1].split(", ")[-1].split()[-1]
            country_code = "CA"
            store_number = poi["id"]
            phone = poi["phone"]
            latitude = poi["latitude"]
            longitude = poi["longitude"]
            hoo = loc_dom.xpath(
                '//p[contains(text(), "Hours")]/following-sibling::table//text()'
            )
            hoo = [e.strip() for e in hoo if e.strip()]
            hours_of_operation = " ".join(hoo) if hoo else ""

            item = SgRecord(
                locator_domain=domain,
                page_url=store_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type="",
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
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
