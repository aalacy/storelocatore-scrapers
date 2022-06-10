import os
import ssl
import json
from lxml import etree
from urllib.parse import urljoin
from time import sleep

from sgselenium import SgChrome
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context


def fetch_data():
    session = SgRequests()
    start_url = "https://www.spinatospizzeria.com/locations-and-menus"
    domain = "spinatospizzeria.com"

    with SgChrome(is_headless=True, seleniumwire_auto_config=False) as driver:
        driver.get(start_url)
        sleep(15)
        dom = etree.HTML(driver.page_source)

        data = (
            dom.xpath('//script[@id="popmenu-apollo-state"]/text()')[0]
            .split("APOLLO_STATE =")[-1]
            .strip()[:-1]
            .split(";\n      window")[0]
        )
        data = json.loads(data)

        all_locations = [k for k in data.keys() if "RestaurantLocation:" in k]
        for k in all_locations:
            poi = data[k]
            poi_html = etree.HTML(poi["customLocationContent"])
            url = poi_html.xpath('.//a[contains(text(), "Menu")]/@href')[0]
            page_url = urljoin(start_url, url)
            loc_response = session.get(page_url)
            loc_dom = etree.HTML(loc_response.text)
            location_type = poi["__typename"]
            if loc_dom.xpath('//span[contains(text(), "Temporarily Closed")]'):
                location_type = "Temporarily Closed"

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=poi["name"],
                street_address=poi["streetAddress"].replace("\n", ""),
                city=poi["city"],
                state=poi["state"],
                zip_postal=poi["postalCode"],
                country_code=poi["country"],
                store_number=poi["id"],
                phone=poi["displayPhone"],
                location_type=location_type,
                latitude=poi["lat"],
                longitude=poi["lng"],
                hours_of_operation=" ".join(poi["schemaHours"]),
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
    if os.environ.get("PROXY_PASSWORD"):
        del os.environ["PROXY_PASSWORD"]

    scrape()
