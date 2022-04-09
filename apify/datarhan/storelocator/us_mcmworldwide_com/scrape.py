from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch


def fetch_data():
    session = SgRequests()
    domain = "mcmworldwide.com"
    start_url = "https://us.mcmworldwide.com/on/demandware.store/Sites-MCM-US-Site/en_US/Stores-FindbyNumberOfStores?format=ajax&noOfStores=10.00&searchType=findbyGeoLocation&searchKey=toronto&showOnlyMcmBoutiquesFlag=true&lat={}&lng={}&source=undefined"

    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.192 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }

    all_coordinates = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=200
    )
    for lat, lng in all_coordinates:
        response = session.get(start_url.format(lat, lng), headers=hdr)
        dom = etree.HTML(response.text)
        all_locations = dom.xpath(
            '//div[@class="mod_accordion js-checkout-storeresult"]/div'
        )

        for poi_html in all_locations:
            location_name = poi_html.xpath(
                './/span[@class="store-name txt-mono"]/text()'
            )
            location_name = location_name[0].strip() if location_name else ""
            raw_address = poi_html.xpath('.//p[@class="store-address"]/span/text()')
            addr = parse_address_intl(" ".join(raw_address))
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            city = addr.city
            country_code = addr.country
            if city and city == "Korea":
                city = ""
                country_code = "Korea"
            state = addr.state
            if state and len(state) > 2:
                continue
            zip_code = addr.postcode
            store_number = poi_html.xpath("@data-store-id")[0]
            phone = poi_html.xpath('.//a[@class="store-phone"]/text()')
            phone = phone[0].replace(" ", "").strip() if phone else ""
            latitude = poi_html.xpath("@data-lat")[0]
            longitude = poi_html.xpath("@data-long")[0]
            hoo = poi_html.xpath('.//div[@class="store-hours"]//text()')
            hoo = [e.strip() for e in hoo if e.strip()][:2]
            hours_of_operation = " ".join(hoo) if hoo else ""
            page_url = "https://us.mcmworldwide.com/en_US/stores/{}/{}".format(
                location_name.lower().replace(" ", "-"), store_number
            )

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
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
