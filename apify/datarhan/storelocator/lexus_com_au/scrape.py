from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.lexus.com.au/lexus-mainsite/api/v1/lexusdealerlookup/dealers/2044/SYDENHAM/null/Sales)"
    domain = "lexus.com.au"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    data = session.get(start_url, headers=hdr).json()

    for poi in data["Data"]:
        hoo = []
        for e in poi["locations"][0]["operatingHours"]:
            hoo.append(f'{e["day"]}: {e["openingTime"]} - {e["closingTime"]}')
        hoo = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.lexus.com.au/contact/find-a-dealer",
            location_name=poi["dealerName"],
            street_address=poi["locations"][0]["streetAddress"],
            city=poi["locations"][0]["suburb"],
            state=poi["locations"][0]["state"],
            zip_postal=poi["locations"][0]["postCode"],
            country_code="AU",
            store_number=poi["dealerCodeSimple"],
            phone=poi["locations"][0]["phone"],
            location_type=poi["serviceType"],
            latitude=poi["locations"][0]["lat"],
            longitude=poi["locations"][0]["lng"],
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
