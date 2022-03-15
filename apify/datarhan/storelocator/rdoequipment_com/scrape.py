# -*- coding: utf-8 -*-
import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "rdoequipment.com"
    start_url = "https://www.rdoequipment.com/rdo-api/branches/query"
    headers = {
        "content-type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36",
    }
    frm = '{"equipmentTypes":[],"pageNumber":"1","pageSize":"200","searchRadius":90000,"Latitude":40.75368539999999,"Longitude":-73.9991637}'
    response = session.post(start_url, headers=headers, data=frm)
    data = json.loads(response.text)

    for poi in data["Items"]:
        store_url = poi["Url"]
        if not store_url:
            continue
        location_name = poi["BranchName"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["Address"]["Street"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["Address"]["City"]
        city = city if city else "<MISSING>"
        state = poi["Address"]["StateCode"]
        state = state if state else "<MISSING>"
        zip_code = poi["Address"]["Zip"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["Address"]["CountryCode"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["BranchId"]
        try:
            phone = json.loads(poi["PhoneNumbers"])[0]["value"]
        except Exception:
            phone = (
                etree.HTML(poi["PhoneNumbers"])
                .xpath("//text()")[0]
                .split("Phone:")[-1]
                .strip()
            )
        location_type = "<MISSING>"
        latitude = poi["Address"]["Latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["Address"]["Longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hoo_data = json.loads(poi["Hours"])
        hoo_data = hoo_data["hourTypes"][0]["schedule"]
        hoo = []
        days_dict = {
            1: "monday",
            2: "tuesday",
            3: "wednesday",
            4: "thursday",
            5: "friday",
            6: "saturday",
            7: "sunday",
        }
        for elem in hoo_data:
            day = days_dict[elem["weekday"]]
            if elem["from"].strip():
                opens = elem["from"]
                closes = elem["to"]
                hoo.append(f"{day} {opens} - {closes}")
            else:
                hoo.append(f"{day} - Closed")
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

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
