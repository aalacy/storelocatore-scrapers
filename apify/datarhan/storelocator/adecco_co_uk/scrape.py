import json
from lxml import etree
from urllib.parse import urljoin
from time import sleep

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgFirefox


def fetch_data():
    session = SgRequests()

    domain = "adecco.co.uk"
    start_url = "https://www.adecco.co.uk/find-a-branch/"
    response = session.post(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@id="nav-tabContent"]//li/a/@href')
    for url in list(set(all_locations)):
        page_url = urljoin(start_url, url)
        with SgFirefox() as driver:
            driver.get(page_url)
            sleep(5)
            loc_dom = etree.HTML(driver.page_source)

        data = loc_dom.xpath('//script[contains(text(), "Latitude")]/text()')
        if data:
            data = data[0].split("details =")[-1].split(";\n")[0]
            poi = json.loads(data)[0]
            hoo = []
            for e in poi["ScheduleList"]:
                day = e["WeekdayId"]
                opens = e["StartTime"].split("T")[-1].replace(":00:00", ":00")
                closes = e["EndTime"].split("T")[-1].replace(":00:00", ":00")
                hoo.append(f"{day} {opens} - {closes}")
            hoo = ", ".join(hoo)
            city = poi["City"]
            location_name = poi["BranchName"]
            street_address = poi["Address"]
            state = poi["State"]
            zip_code = poi["ZipCode"]
            country_code = poi["CountryCode"]
            store_number = poi["BranchCode"]
            phone = poi["PhoneNumber"]
            latitude = poi["Latitude"]
            longitude = poi["Longitude"]
        else:
            data = loc_dom.xpath('//script[contains(text(), "streetAddress")]/text()')
            if not data:
                continue
            poi = json.loads(data[0])[0]
            hoo = ""
            city = poi["address"]["addressLocality"]
            location_name = poi["name"]
            street_address = poi["address"]["streetAddress"]
            state = poi["address"]["addressRegion"]
            zip_code = poi["address"]["postalCode"]
            country_code = poi["address"]["addressCountry"]
            store_number = ""
            phone = poi["telephone"]
            geo = (
                loc_dom.xpath('//a[contains(@href, "maps/@")]/@href')[0]
                .split("@")[-1]
                .split(",")[:2]
            )
            latitude = geo[0]
            longitude = geo[1]

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type="",
            latitude=latitude,
            longitude=longitude,
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
