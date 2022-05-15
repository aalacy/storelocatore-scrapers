# -*- coding: utf-8 -*-
import json
from lxml import etree
from time import sleep

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgFirefox


def fetch_data():
    session = SgRequests()
    start_url = "https://mominokitokyojapaneselifestyle.com/pages/store-location"
    domain = "mominokitokyojapaneselifestyle.com"

    with SgFirefox() as driver:
        driver.get(start_url)
        sleep(25)
        frame = driver.find_element_by_xpath('//iframe[@title="powr map"]')
        driver.switch_to.frame(frame)
        dom = etree.HTML(driver.page_source)
    data = (
        dom.xpath('//script[contains(text(), "window.CONTENT=")]/text()')[0]
        .split("CONTENT=")[1]
        .split("window")[0]
        .strip()[:-1]
    )
    data = json.loads(data)

    response = session.get(
        "https://mominokitokyojapaneselifestyle.com/pages/find-a-store-hours"
    )
    h_dom = etree.HTML(response.text)
    all_hoo = h_dom.xpath(
        '//h1[contains(text(), "Store Open Hours")]/following-sibling::div//text()'
    )
    all_hoo = [e.strip() for e in all_hoo if e.strip()]
    for poi in data["locations"]:
        location_name = poi["name"]
        raw_address = poi["address"].split(", ")
        for i, hours in enumerate(all_hoo):
            if location_name.split("Lifestyle")[-1].strip() in hours:
                starts = i

        all_days = [
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
            "Monday",
            "Tuesday",
        ]
        hoo = []
        for e in all_hoo[starts + 1 :]:
            check = False
            for day in all_days:
                if day in e:
                    check = True
                elif "am —" in e:
                    check = True
            if not check:
                break
            hoo.append(e)
        hoo = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=raw_address[0],
            city=raw_address[1],
            state=raw_address[2].split()[0],
            zip_postal=raw_address[2].split()[-1],
            country_code=raw_address[-1],
            store_number="",
            phone=poi["number"],
            location_type="",
            latitude=poi["lat"],
            longitude=poi["lng"],
            hours_of_operation=hoo,
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
