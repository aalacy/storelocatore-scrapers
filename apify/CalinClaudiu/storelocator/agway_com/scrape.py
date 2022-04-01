from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.agway.com/app/extensions/RSM/EnhancedStoreLocator/1.0.0/services/EnhancedStoreLocator.Service.ss?c=6952524&latitude=38.8937336&longitude=-77.0846157&n=2&order=-1&page=all&results_per_page=100&sort=distance"
    domain = "agway.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    all_locations = session.get(start_url, headers=hdr).json()
    for poi in all_locations:
        if poi["isBranded"] == "F":
            continue
        street_address = poi["address1"]
        if poi["address2"]:
            street_address += " " + poi["address2"]

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.agway.com/agway-stores",
            location_name=poi["name"],
            street_address=street_address,
            city=poi["city"],
            state=poi["state"],
            zip_postal=poi["zip"],
            country_code=poi["country"],
            store_number=poi["internalid"],
            phone=poi["phone"],
            location_type=poi["isBranded"],
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
