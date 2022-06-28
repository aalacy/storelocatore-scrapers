from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    domain = "adecco.fr"
    start_url = "https://www.adecco.fr/agences-emploi/branches/"
    frm = {"dto": {"MaxResults": "5000", "Industry": "ALL", "RadiusUnits": "KM"}}
    data = session.post(
        "https://www.adecco.fr/globalweb/branch/branchsearch", json=frm
    ).json()
    for poi in data["Items"]:
        page_url = urljoin(start_url, poi["ItemUrl"])
        street_address = f'{poi["Address"]} {poi["AddressExtension"]}'
        hoo = []
        for e in poi["ScheduleList"]:
            day = e["WeekdayId"]
            opens = e["StartTime"].split("T")[-1].replace("0:00", "0")
            closes = e["EndTime"].split("T")[-1].replace("0:00", "0")
            hoo.append(f"{day}: {opens} - {closes}")
        hoo = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["MetaTitle"],
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
