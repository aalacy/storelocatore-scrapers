import re
import json
from lxml import etree
from urllib.parse import urljoin
from time import sleep

from sgselenium import SgFirefox
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    start_url = "https://www.worldwidegolfshops.com/the-golf-mart"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")

    with SgFirefox() as driver:
        driver.get(start_url)
        sleep(15)
        dom = etree.HTML(driver.page_source)
        data = dom.xpath('//script[contains(text(), "find-a-store")]/text()')[2].split(
            "__RUNTIME__ ="
        )[-1]
        data = json.loads(data)
        all_poi = []
        for k, v in data.items():
            if (
                "StoreLocationGolfMartContainer/flex-layout.col#StoreLocationGolfMartCol/flex-layout.row"
                in k
            ):
                all_poi.append(v)

        all_locations = []
        for poi in all_poi:
            if not poi["content"].get("text"):
                continue
            poi_html = etree.HTML(poi["content"]["text"])
            url = poi_html.xpath(".//a/@href")
            if url:
                all_locations.append(url[0])

        for url in all_locations:
            page_url = urljoin(start_url, url)
            driver.get(page_url)
            sleep(10)
            loc_dom = etree.HTML(driver.page_source)
            poi = loc_dom.xpath('//script[contains(text(), "address")]/text()')[0]
            poi = json.loads(poi)
            location_name = loc_dom.xpath(
                '//h1[@class="vtex-yext-store-locator-0-x-storeTitle tc"]/text()'
            )[0]
            hoo = []
            for e in poi["openingHoursSpecification"]:
                hoo.append(f'{e["dayOfWeek"]} {e["opens"]} {e["closes"]}')
            hours_of_operation = " ".join(hoo)

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=poi["address"]["streetAddress"],
                city=poi["address"]["addressLocality"],
                state=poi["address"]["addressRegion"],
                zip_postal=poi["address"]["postalCode"],
                country_code=SgRecord.MISSING,
                store_number=poi["@id"],
                phone=poi["telephone"],
                location_type=poi["@type"][0],
                latitude=poi["geo"]["latitude"],
                longitude=poi["geo"]["longitude"],
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
