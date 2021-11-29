import re
import json
from lxml import etree
from time import sleep
from urllib.parse import urljoin

from sgselenium.sgselenium import SgFirefox
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    start_url = "https://www.worldwidegolfshops.com/vans-golf-shops"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")

    session = SgRequests()
    response = session.get(start_url)
    dom = etree.HTML(response.text)
    data = dom.xpath('//script[contains(text(), "store.custom.find-a-store")]/text()')[
        2
    ]
    data = json.loads(data)
    all_poi = []
    for k, v in data.items():
        if "find-a-store-vans-col" in k:
            all_poi.append(v)

    all_locations = []
    for poi in all_poi:
        if poi["props"].get("text"):
            try:
                all_locations.append(
                    poi["props"]["text"].split("](")[1].split(")\n")[0]
                )
            except Exception:
                continue

    for url in all_locations:
        page_url = urljoin(start_url, url)
        if "##" in page_url:
            continue

        with SgFirefox() as driver:
            driver.get(page_url)
            sleep(5)
            loc_dom = etree.HTML(driver.page_source)
        poi = loc_dom.xpath('//script[contains(text(), "address")]/text()')[0]
        poi = json.loads(poi)
        location_name = loc_dom.xpath("//h1/text()")
        if not location_name:
            continue
        location_name = location_name[0]
        hoo = []
        for e in poi["openingHoursSpecification"]:
            if not e.get("dayOfWeek"):
                continue
            if not e.get("opens"):
                hoo.append(f'{e["dayOfWeek"]} closed')
            else:
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
