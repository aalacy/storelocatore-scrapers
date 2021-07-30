import re
import demjson
from lxml import etree

from sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sgscrape.sgpostal import parse_address_intl
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    # Your scraper here
    session = SgRequests()

    domain = "eurosparni.co.uk"
    start_url = "https://www.eurosparni.co.uk/nearest-store?postcode={}"

    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.BRITAIN], expected_search_radius_miles=10
    )
    for code in all_codes:
        store_url = start_url.format(code)
        response = session.get(store_url)
        dom = etree.HTML(response.text)
        all_locations = dom.xpath(
            '//div[@class="owl-item" and div[@class="large-7 large-offset-1 columns"]]'
        )

        for i, poi_html in enumerate(all_locations):
            store_url = "https://www.eurosparni.co.uk/nearest-store"
            location_name = poi_html.xpath('.//h1[@id="storeName"]/text()')
            if not location_name:
                continue
            location_name = location_name[0]
            raw_address = poi_html.xpath(
                './/h1[@id="storeName"]/following-sibling::p//text()'
            )
            raw_address = " ".join([e.strip() for e in raw_address if e.strip()])
            addr = parse_address_intl(raw_address)
            street_address = raw_address.split(",")[0]
            city = addr.city
            city = city if city else "<MISSING>"
            zip_code = " ".join(raw_address.split()[-2:])
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = addr.country
            country_code = country_code if country_code else "<MISSING>"
            phone = poi_html.xpath('.//a[contains(@href, "tel")]/@href')
            phone = phone[0].split(":")[-1] if phone else "<MISSING>"
            geo = re.findall(r"location\d = (.+?);", response.text)[i]
            geo = demjson.decode(geo)
            latitude = geo["lat"]
            longitude = geo["lng"]
            hoo = poi_html.xpath(
                './/h5[contains(text(), "Opening Hours")]/following-sibling::table//text()'
            )
            hoo = [e.strip() for e in hoo if e.strip()][3:]
            hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

            if zip_code == "2h L":
                zip_code = "BT22 2hL"
            if "Co. Down" in zip_code:
                zip_code = "<MISSING>"

            street_address = street_address.split(city)[0].strip()
            if city.upper() in street_address:
                street_address = street_address.split(city.upper())[0].strip()

            item = SgRecord(
                locator_domain=domain,
                page_url=store_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=SgRecord.MISSING,
                zip_postal=zip_code,
                country_code=country_code,
                store_number=SgRecord.MISSING,
                phone=phone,
                location_type=SgRecord.MISSING,
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
