# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.haglofs.com/api/content/en/stores"
    domain = "haglofs.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    data = session.get(start_url, headers=hdr).json()
    for poi in data["stores"]:
        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.haglofs.com/en/stores",
            location_name=poi["name"],
            street_address=poi["address"]["street"],
            city=poi["address"]["city"],
            state="",
            zip_postal=poi["address"]["zipCode"],
            country_code="",
            store_number="",
            phone=poi["phone"],
            location_type="",
            latitude=poi["coordinates"]["latitude"],
            longitude=poi["coordinates"]["longitude"],
            hours_of_operation=" ".join(poi["openingHours"]),
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
