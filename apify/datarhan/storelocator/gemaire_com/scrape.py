import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "gemaire.com"
    start_url = "https://www.gemaire.com/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    data = dom.xpath('//script[contains(text(), "reactBranchConfig")]/text()')[0].split(
        "Config="
    )[-1][:-1]
    data = json.loads(data)

    for store_number, poi in data["allBranches"].items():
        hoo = []
        days = {
            "1": "Monday",
            "2": "Tuesday",
            "3": "Wendsday",
            "4": "Thursday",
            "5": "Friday",
            "6": "Satarday",
            "7": "Sunday",
        }
        for day, hours in poi["formatted_hours"].items():
            day = days[day]
            if hours["isOpen"]:
                opens = hours["open"]
                closes = hours["close"]
                hoo.append(f"{day} {opens} - {closes}")
            else:
                hoo.append(f"{day} closed")
        hoo = " ".join(hoo) if hoo else ""
        latitude = poi["latitude"] if poi["latitude"] != 0 else ""
        longitude = poi["longitude"] if poi["longitude"] != 0 else ""

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=poi["branch_name"],
            street_address=poi["address"]["address_2"],
            city=poi["address"]["city"],
            state=poi["address"]["state"],
            zip_postal=poi["address"]["postcode"],
            country_code=poi["address"]["country"],
            store_number=store_number,
            phone=poi["address"]["phone"],
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
