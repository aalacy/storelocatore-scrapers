from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://toyota-api.azure-api.net/lexus-middleware-live/suppliers?filter[where][supplierType]=dealer&filter[where][lexusSupplier]=Y"
    domain = "lexus.co.za"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    all_locations = session.get(start_url, headers=hdr).json()
    for poi in all_locations:
        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.lexus.co.za/locate-dealer",
            location_name=poi["name"],
            street_address=poi["streetAddress"],
            city=poi["city"],
            state=poi["province"],
            zip_postal=poi["postCode"],
            country_code="",
            store_number=poi["supplierId"],
            phone=poi["telephone"],
            location_type=poi["supplierType"],
            latitude=poi["lat"],
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
