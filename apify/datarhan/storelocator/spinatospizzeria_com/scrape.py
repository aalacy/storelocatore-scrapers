import os
import json
from lxml import etree
from urllib.parse import urljoin
import time

from sgselenium import SgChrome
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    start_url = "https://www.spinatospizzeria.com/locations-and-menus"
    domain = "spinatospizzeria.com"

    driver = SgChrome(is_headless=False).driver()

    driver.get(start_url)
    time.sleep(15)
    dom = etree.HTML(driver.page_source)
    driver.quit()

    data = (
        dom.xpath('//script[@id="popmenu-apollo-state"]/text()')[0]
        .split("APOLLO_STATE =")[-1]
        .strip()[:-1]
    )
    data = json.loads(data)

    all_locations = [k for k in data.keys() if "RestaurantLocation:" in k]
    for k in all_locations:
        poi = data[k]
        page_url = urljoin(start_url, poi["slug"])

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
            location_type=poi["__typename"],
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
