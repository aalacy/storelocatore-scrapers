import json

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "adeccousa.com"
    start_url = "https://www.adeccousa.com/globalweb/branch/branchsearch"

    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Content-Type": "application/json; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }

    body = '{"dto":{"Latitude":"34.1030032","Longitude":"-118.4104684","MaxResults":"1000","Radius":"50000","Industry":"ALL","RadiusUnits":"MILES"}}'
    response = session.post(start_url, data=body, headers=headers)
    data = json.loads(response.text)

    for poi in data["Items"]:
        store_url = "https://www.adeccousa.com/" + poi["ItemUrl"]
        store_url = store_url if store_url else "<MISSING>"
        location_name = poi["BranchName"]
        if "test" in location_name:
            continue
        street_address = poi["Address"]
        if poi["AddressExtension"]:
            street_address += ", " + poi["AddressExtension"]
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
            city=poi["City"],
            state=poi["State"],
            zip_postal=poi["ZipCode"],
            country_code=poi["CountryCode"],
            store_number=poi["BranchCode"],
            phone=poi["PhoneNumber"],
            location_type="",
            latitude=poi["Latitude"],
            longitude=poi["Longitude"],
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
