import json
from time import sleep
from lxml import etree

from sgselenium.sgselenium import webdriver
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter

profile = webdriver.FirefoxProfile()
profile.set_preference(
    "geo.wifi.uri",
    'data:application/json,{"location": {"lat": 38.912650, "lng":-77.036185}, "accuracy": 20.0}',
)
profile.set_preference("geo.prompt.testing", True)
options = webdriver.FirefoxOptions()
options.headless = True


def fetch_data():
    domain = "cashwise.com"
    start_url = "https://www.cashwise.com/storelocator"

    driver = webdriver.Firefox(profile, options=options)
    driver.get(start_url)
    sleep(20)
    dom = etree.HTML(driver.page_source)

    all_locations = dom.xpath("//script[@data-yext-id]/text()")
    for poi in all_locations:
        poi = json.loads(poi)
        page_url = poi.get("url")
        location_name = poi["name"]
        street_address = poi["address"]["streetAddress"]
        city = poi["address"]["addressLocality"]
        state = poi["address"]["addressRegion"]
        zip_code = poi["address"]["postalCode"]
        store_number = poi["@id"]
        phone = poi["telephone"]
        location_type = ", ".join(poi["@type"])
        latitude = poi["geo"]["latitude"]
        longitude = poi["geo"]["longitude"]
        hours_of_operation = []
        for elem in poi["openingHoursSpecification"]:
            day = elem["dayOfWeek"]
            if elem.get("opens"):
                hours_of_operation.append(f'{day} {elem["opens"]} - {elem["closes"]}')
            else:
                hours_of_operation.append(f"{day} closed")
        hours_of_operation = " ".join(hours_of_operation) if hours_of_operation else ""

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code="",
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
