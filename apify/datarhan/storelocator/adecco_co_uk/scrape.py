import json
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    domain = "adecco.co.uk"
    start_url = "https://www.adecco.co.uk/find-a-branch/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@id="nav-tabContent"]//li/a/@href')
    for url in list(set(all_locations)):
        store_url = urljoin(start_url, url)
        if "branches" in url:
            continue
        print(store_url)
        loc_response = session.get(store_url)
        if loc_response.status_code != 200:
            continue
        loc_dom = etree.HTML(loc_response.text)
        poi = loc_dom.xpath('//script[contains(text(), "branch_details =")]/text()')
        if not poi:
            continue
        if (
            poi
            and poi[0].split("branch_details =")[-1].split(";\r\n")[0].strip() == "[]"
        ):
            continue
        poi = json.loads(poi[0].split("branch_details =")[-1].split(";\r\n")[0])[0]

        location_name = poi["BranchName"]
        street_address = poi["Address"]
        if poi["AddressExtension"]:
            street_address += ", " + poi["AddressExtension"]
        city = poi["City"]
        city = city if city else "<MISSING>"
        state = poi["State"]
        state = state if state else "<MISSING>"
        zip_code = poi["ZipCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["CountryCode"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["BranchCode"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["PhoneNumber"]
        phone = phone if phone else "<MISSING>"
        location_type = ""
        location_type = location_type if location_type else "<MISSING>"
        latitude = poi["Latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["Longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = []
        for elem in poi["ScheduleList"]:
            day = elem["WeekdayId"]
            opens = elem["StartTime"].split("T")[-1]
            closes = elem["EndTime"].split("T")[-1]
            hours_of_operation.append("{} {} - {}".format(day, opens, closes))
        hours_of_operation = (
            ", ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
        )

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
