# -*- coding: utf-8 -*-
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


def fetch_data():
    session = SgRequests()

    start_url = "https://www.peakpharmacy.co.uk/pharmacy-results/?lat={}&long={}"
    domain = "murrays.co.uk"

    all_coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.BRITAIN], expected_search_radius_miles=10
    )
    for lat, lng in all_coords:
        response = session.get(start_url.format(lat, lng))
        dom = etree.HTML(response.text)
        all_locations = dom.xpath('//div[@class="pharmacy-results-list"]/a')
        for poi_html in all_locations:
            location_name = poi_html.xpath("@data-branch-name")[0]
            phone = poi_html.xpath("@data-branch-telephone")[0]
            page_url = poi_html.xpath("@data-branch-url")[0]
            raw_address = poi_html.xpath("@data-branch-address")[0]
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += ", " + addr.street_address_2
            hoo = etree.HTML(poi_html.xpath("@data-opening-hours")[0]).xpath("//text()")
            hoo = " ".join([e.strip() for e in hoo if e.strip()])
            zip_code = addr.postcode
            if not zip_code:
                zip_code = raw_address.split(", ")[-1]
                if len(zip_code.split()) > 2:
                    zip_code = " ".join(zip_code.split()[-2:])

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=zip_code,
                country_code="",
                store_number="",
                phone=phone,
                location_type="",
                latitude="",
                longitude="",
                hours_of_operation=hoo,
                raw_address=raw_address,
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
