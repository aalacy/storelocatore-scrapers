# -*- coding: utf-8 -*-
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

    start_url = "https://www.adecco.pl/pl-pl/locations/"
    domain = "adecco.pl"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//a[@class="list-tab-links"]/@href')
    for url in all_locations:
        page_url = urljoin(start_url, url)
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        data = (
            loc_dom.xpath('//script[contains(text(), "branch_details")]/text()')[0]
            .split("branch_details =")[1]
            .split("var brand_Logo")[0]
            .strip()[:-1]
        )
        all_poi = json.loads(data)
        for poi in all_poi:
            page_url = urljoin(start_url, poi["SeoBranchUrl"])
            hoo = []
            for e in poi["ScheduleList"]:
                day = e["WeekdayId"]
                opens = e["StartTime"].split("T")[1][:-3]
                closes = e["EndTime"].split("T")[1][:-3]
                hoo.append(f"{day}: {opens} - {closes}")
            hoo = " ".join(hoo)
            phone = poi["PhoneNumber"].split("/")[0]
            if ":" in phone:
                phone = phone.split(":")[1].split(";")[0]
            phone = phone.split(";")[0].split("ciu")[-1]

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=poi["BranchName"],
                street_address=poi["Address"],
                city=poi["City"],
                state=poi["State"],
                zip_postal=poi["ZipCode"],
                country_code=poi["CountryCode"],
                store_number=poi["BranchCode"],
                phone=phone,
                location_type="",
                latitude=poi["Latitude"],
                longitude=poi["Longitude"],
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
