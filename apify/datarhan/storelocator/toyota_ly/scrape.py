from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://toyota.ly/wp-json/toyota/dealer/v1"
    domain = "toyota.ly"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    all_locations = session.get(start_url, headers=hdr).json()
    for store_number, poi in all_locations.items():
        phone = [
            e["dealer_phone"]
            for e in poi["dealer_phones"]
            if e["dealer_phone_type"] == "Sales"
        ]
        phone = phone[0] if phone else ""
        hoo = []
        for e in poi["working_hours"]:
            f_day = e["from_day"]
            t_day = e["to_day"]
            f_hour = e["from_hour"]
            t_hour = e["to_hour"]
            hoo.append(f"{f_day} - {t_day}: {f_hour} - {t_hour}")
        hoo = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url="https://toyota.ly/find-a-dealer/",
            location_name=poi["title"],
            street_address=poi["dealer_address"],
            city=poi["map"].get("city"),
            state=poi["map"].get("state"),
            zip_postal="",
            country_code=poi["map"].get("country_short"),
            store_number=store_number,
            phone=phone,
            location_type="",
            latitude=poi["map"]["lat"],
            longitude=poi["map"]["lng"],
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
