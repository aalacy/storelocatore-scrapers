from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://suzuki.pl/auto/dealerzy?json=)"
    domain = "suzuki.pl"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    all_locations = session.get(start_url, headers=hdr).json()
    for poi in all_locations:
        if poi["is_auto"] != "1":
            continue

        item = SgRecord(
            locator_domain=domain,
            page_url="https://suzukiqld.com.au/locate/",
            location_name=poi["name"],
            street_address=poi["street"],
            city=poi["city"],
            state="",
            zip_postal=poi["postal_code"],
            country_code="PL",
            store_number=poi["id"],
            phone=poi["phones"][0].split("wew")[0].strip(),
            location_type="",
            latitude=poi["lat"],
            longitude=poi["lng"],
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
