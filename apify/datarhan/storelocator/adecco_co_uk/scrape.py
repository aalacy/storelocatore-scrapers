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
    response = session.post(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@id="nav-tabContent"]//li/a/@href')
    all_locations.append(
        "https://www.adecco.co.uk/find-a-branch/branches/grey-street-newcastle-upon-tyne-uk?location=grey%20street+%20newcastle%20upon%20tyne+%20uk&distance=50&latitude=54.9724619&longitude=-1.6123224"
    )
    for url in list(set(all_locations)):
        url = urljoin(start_url, url)
        response = session.get(url)
        dom = etree.HTML(response.text)

        data = dom.xpath('//script[contains(text(), "branch_details")]/text()')
        if not data:
            continue
        data = data[0].split("details =")[-1].split(";\r\n    var brand")[0]
        data = json.loads(data)
        for poi in data:
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
                location_name=poi["BranchName"],
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
