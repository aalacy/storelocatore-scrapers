import re
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


def fetch_data():
    session = SgRequests()
    domain = "optumcare.com"
    actions = [
        "search-urgent-care",
        "search-hospitals",
        "search-labs",
        "search-facilities",
    ]
    all_coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=50
    )
    for lat, lng in all_coords:
        for action in actions:
            url = "https://lookup.optumcare.com/locations-results/?lat={}&lng={}&action={}&side=1&location-office-zip=&radius=50"
            response = session.get(url.format(lat, lng, action))
            all_locations = re.findall(r"d_object\((.+?)\);", response.text)
            for poi in all_locations:
                poi = [e.replace('"', "") for e in poi.split(",")]
                if len(poi) == 13:
                    del poi[2]
                page_url = "https://lookup.optumcare.com" + poi[10]

                item = SgRecord(
                    locator_domain=domain,
                    page_url=page_url,
                    location_name=poi[1],
                    street_address=poi[3],
                    city=poi[4],
                    state=poi[5],
                    zip_postal=poi[6],
                    country_code="",
                    store_number=poi[0],
                    phone=poi[2],
                    location_type="",
                    latitude=poi[7],
                    longitude=poi[8],
                    hours_of_operation="",
                )

                yield item

    response = session.get("https://www.optumcare.com/state-networks/locations.html")
    dom = etree.HTML(response.text)

    all_states = dom.xpath('//a[contains(text(), "Find care")]/@href')
    for url in all_states:
        response = session.get(url)
        dom = etree.HTML(response.text)
        regions = dom.xpath('//b/a[contains(text(), "Primary care clinics")]/@href')
        for url in regions:
            response = session.get(url)
            dom = etree.HTML(response.text)

            all_locations = dom.xpath(
                '//div[div[h2[contains(text(), "Primary Care locations")]]]/following-sibling::div//a[contains(@href, "primary-care-locations")]/@href'
            )
            for page_url in all_locations:
                loc_response = session.get(page_url)
                loc_dom = etree.HTML(loc_response.text)

                location_name = loc_dom.xpath("//h1/b/span/text()")
                if not location_name:
                    location_name = loc_dom.xpath("//h4/b/text()")
                if not location_name:
                    location_name = loc_dom.xpath("//h1/strong/span/text()")
                if not location_name:
                    location_name = loc_dom.xpath("//h4/strong/text()")
                location_name = location_name[0].replace("\xa0", " ")
                raw_address = loc_dom.xpath(
                    '//div[@class="text-component text-inner"]/p[1]/text()'
                )[:2]
                if "Acacia Internal" in raw_address[0]:
                    raw_address = loc_dom.xpath(
                        '//div[@class="text-component text-inner"]/p[2]/text()'
                    )[:2]
                if "Ave." in raw_address[1]:
                    raw_address = [
                        ", ".join([e.strip() for e in raw_address if e.strip()])
                    ] + [
                        loc_dom.xpath(
                            '//div[@class="text-component text-inner"]/p[1]/text()'
                        )[2]
                    ]
                phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')[0]
                hoo = loc_dom.xpath('//p[b[contains(text(), "Hours")]]/text()')
                hoo = " ".join([e.strip() for e in hoo])

                item = SgRecord(
                    locator_domain=domain,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=raw_address[0],
                    city=raw_address[1].split(", ")[0],
                    state=raw_address[1].split(", ")[-1].split()[0],
                    zip_postal=raw_address[1].split(", ")[-1].split()[-1],
                    country_code="",
                    store_number="",
                    phone=phone,
                    location_type="",
                    latitude="",
                    longitude="",
                    hours_of_operation="",
                )

                yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            ),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
