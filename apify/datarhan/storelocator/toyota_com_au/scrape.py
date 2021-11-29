from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.toyota.com.au/support/find-a-dealer"
    domain = "toyota.com.au"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_states = dom.xpath("//@data-ng-value")
    for state in all_states:
        url = f"https://www.toyota.com.au/main/api/v1/toyotaforms/info/dealersbystate/{state[1:-1]}?dealerOptIn=false"
        data = session.get(url).json()

        for poi in data["results"]:
            if not poi["sales"]:
                continue
            page_url = poi["webSite"]
            if not page_url:
                page_url = "https://www.toyota.com.au/support/find-a-dealer"

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=poi["name"],
                street_address=poi["address"],
                city=poi["city"],
                state=poi["state"],
                zip_postal=poi["postCode"],
                country_code="AU",
                store_number=poi["sapDealerCode"],
                phone=poi["telephone"],
                location_type="",
                latitude=poi["refX"],
                longitude=poi["refY"],
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
