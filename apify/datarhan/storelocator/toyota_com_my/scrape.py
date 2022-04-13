from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://toyota.com.my/get-source?data=service-locator-dealer"
    domain = "toyota.com.my"
    hdr = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:94.0) Gecko/20100101 Firefox/94.0",
        "Accept": "*/*",
        "X-Requested-With": "XMLHttpRequest",
    }

    all_locations = session.get(start_url, headers=hdr).json()
    for poi in all_locations:
        if not poi["sales"] == "1":
            continue
        page_url = "https://toyota.com.my/aftersales-services/service-locator"

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["company_name"],
            street_address=poi["address"],
            city=poi["district"],
            state=poi["state"],
            zip_postal=poi["postcode"],
            country_code="MY",
            store_number=poi["id"],
            phone=poi["phone_1"],
            location_type="",
            latitude=poi["latitude"],
            longitude=poi["longitude"],
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
