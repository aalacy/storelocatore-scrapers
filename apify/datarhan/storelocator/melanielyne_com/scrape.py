# -*- coding: utf-8 -*-
import json
from lxml import etree

from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://www.melanielyne.com/en/stores-list/?dwfrm_storelocator_countryCode=CANADA&dwfrm_storelocator_distanceUnit=kilometers&dwfrm_storelocator_maxdistance=200&dwfrm_storelocator_lat=&dwfrm_storelocator_long=&dwfrm_storelocator_mapZoom=&dwfrm_storelocator_mapCenter=&dwfrm_storelocator_mapBounds=&dwfrm_storelocator_location={}&dwfrm_storelocator_storeType=&dwfrm_storelocator_findbyzip=Search"
    domain = "melanielyne.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.CANADA], expected_search_radius_miles=50
    )
    scraped_urls = []
    for code in all_codes:
        response = session.get(start_url.format(code), headers=hdr)
        dom = etree.HTML(response.text)
        all_locations = dom.xpath("//tr[@data-store-details]")

        for poi_html in all_locations:
            poi = json.loads(poi_html.xpath("@data-store-details")[0])
            store_url = (
                "https://www.melanielyne.com/en/store-details/?StoreID={}".format(
                    poi["id"]
                )
            )
            if store_url in scraped_urls:
                continue
            scraped_urls.append(store_url)
            loc_response = session.get(store_url)
            loc_dom = etree.HTML(loc_response.text)

            location_name = poi["name"]
            location_name = location_name if location_name else "<MISSING>"
            raw_address = poi_html.xpath('.//div[@class="address-details"]/text()')
            raw_address = [e.strip() for e in raw_address if e.strip()]
            addr = parse_address_intl(" ".join(raw_address))
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            city = addr.city
            state = addr.state
            if not state:
                state = " ".join(raw_address[-1].split(", ")[-1].split()[:-1])
            zip_code = json.loads(
                loc_dom.xpath('//div[@id="store-details-map"]/@data-store')[0]
            )["zip"]
            country_code = "CA"
            store_number = poi["id"]
            phone = poi["phone"]
            phone = phone if phone else "<MISSING>"
            location_type = "<MISSING>"
            latitude = poi["latitude"]
            longitude = poi["longitude"]
            hoo = loc_dom.xpath(
                '//p[contains(text(), "Hours")]/following-sibling::table//text()'
            )
            hoo = [e.strip() for e in hoo if e.strip()]
            hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"
            if street_address == "184":
                street_address = "184 Laura - Edmonton Airport Outlets"

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
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=" ".join(raw_address),
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
