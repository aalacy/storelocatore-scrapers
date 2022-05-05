import json

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.marutisuzuki.com/api/dealerlocators"
    domain = "marutisuzuki.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    frm = {"Category": "dealer", "CityName": "Delhi", "Radius": 30000}
    data = session.post(start_url, headers=hdr, data=frm).json()

    results = json.loads(data["Result"]["Response"])
    for poi in results["list"]:

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.marutisuzuki.com/dealer-showrooms",
            location_name=poi["dealername"],
            street_address=poi["dealeraddress"],
            city=poi["cityname"],
            state=poi["statename"],
            zip_postal="",
            country_code="India",
            store_number=poi["dealercode"],
            phone=poi["dealerphone1"],
            location_type=poi["category"],
            latitude="",
            longitude="",
            hours_of_operation="",
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
