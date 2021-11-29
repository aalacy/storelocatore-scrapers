from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    domain = "adecco.co.uk"
    start_url = "https://www.adecco.co.uk/globalweb/branch/branchsearch"

    frm = {
        "dto": {
            "Industry": "ALL",
            "Latitude": "54.9951837",
            "Longitude": "-1.5666991",
            "MaxResults": "100",
            "Radius": "50000",
            "RadiusUnits": "MILES",
        }
    }
    response = session.post(start_url, json=frm).json()

    for poi in response["Items"]:
        page_url = urljoin(start_url, poi["SeoCityUrl"])
        street_address = poi["Address"]
        if poi["AddressExtension"]:
            street_address += " " + poi["AddressExtension"]
        hoo = []
        for e in poi["ScheduleList"]:
            opens = e["StartTime"].split("T")[-1][:-3]
            closes = e["EndTime"].split("T")[-1][:-3]
            hoo.append(f'{e["WeekdayId"]} {opens} - {closes}')
        hoo = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["BranchName"],
            street_address=street_address,
            city=poi["City"],
            state=SgRecord.MISSING,
            zip_postal=poi["ZipCode"],
            country_code=poi["CountryCode"],
            store_number=poi["BranchCode"],
            phone=poi["PhoneNumber"],
            location_type=SgRecord.MISSING,
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
