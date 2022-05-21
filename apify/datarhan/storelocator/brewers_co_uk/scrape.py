import re
import json
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
    domain = "brewers.co.uk"
    start_url = "https://www.brewers.co.uk/stores/{}"
    scraped_items = []
    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.BRITAIN], expected_search_radius_miles=10
    )
    for code in all_codes:
        response = session.get(start_url.format(code.replace(" ", "%20")))
        dom = etree.HTML(response.text)

        all_locations = dom.xpath('//a[contains(@href, "/stores/")]/@href')
        all_locations = [e.lower().strip() for e in all_locations]
        for url in list(set(all_locations)):
            store_url = urljoin(start_url, url)
            if store_url in scraped_items:
                continue
            scraped_items.append(store_url)
            loc_response = session.get(store_url)
            if loc_response.status_code != 200:
                continue
            loc_dom = etree.HTML(loc_response.text)
            data = loc_dom.xpath("//@ng-init")
            if not data:
                continue
            data = data[0]
            data = re.findall(r"initSingle\((.+)\)", data)[0]
            poi = json.loads(data)[0]

            location_name = loc_dom.xpath('//h1[@class="inline h2"]/text()')
            location_name = (
                " ".join(location_name[0].split()).strip() if location_name else ""
            )
            street_address = poi["address1"]
            if poi["address2"]:
                street_address += " " + poi["address2"]
            street_address = " ".join(
                [elem.strip() for elem in street_address.split() if elem.strip()]
            ).replace("  ", " ")
            city = poi["city"]
            state = poi["county"]
            zip_code = poi["postcode"]
            country_code = poi["country"]
            store_number = poi["id"]
            phone = poi["phone"]
            location_type = "<MISSING>"
            latitude = poi["latitude"]
            longitude = poi["longitude"]
            hoo = loc_dom.xpath('//dl[@class="inline"]//text()')
            hoo = [" ".join(elem.split()) for elem in hoo if elem.strip()]
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
                location_type=location_type,
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
