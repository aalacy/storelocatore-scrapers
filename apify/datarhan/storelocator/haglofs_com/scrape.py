# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.haglofs.com/on/demandware.store/Sites-haglofs-eu-Site/de_AT/Stores-GetNearestStores?latitude=48.2081743&longitude=16.3738189&countryCode=AT&distanceUnit=km&maxdistance=50000&brands=hg&isDisableCheckRTI=true"
    domain = "haglofs.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    data = session.get(start_url, headers=hdr).json()
    for store_number, poi in data["stores"].items():
        street_address = poi["address1"]
        if poi["address2"]:
            street_address += ", " + poi["address2"]

        item = SgRecord(
            locator_domain=domain,
            page_url=poi["storeUrl"],
            location_name=poi["name"],
            street_address=street_address,
            city=poi["city"],
            state=poi["stateCode"],
            zip_postal=poi["postalCode"],
            country_code=poi["countryCode"],
            store_number=store_number,
            phone=poi["phone"],
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
