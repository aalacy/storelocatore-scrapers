from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://platform.suzuki-motor.ru/catalog/dealers/"
    domain = "suzuki-motor.ru"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    data = session.get(start_url, headers=hdr).json()
    for poi in data["dealers"]:
        poi = poi["centers"]["centers"][0]
        raw_address = poi["location"]["address"]
        try:
            location_type = ", ".join(
                [e["service"] for e in poi["workinghours"][0]["services"]]
            )
        except Exception:
            location_type = ", ".join([e for e in poi["workinghours"][0]["services"]])
        if "автомобили" not in location_type:
            continue

        item = SgRecord(
            locator_domain=domain,
            page_url="https://suzuki-motor.ru/buy/new-auto/dealers/",
            location_name=poi["name"],
            street_address=poi["location"]["query"],
            city=raw_address.split(", ")[1],
            state="",
            zip_postal="",
            country_code="RU",
            store_number="",
            phone=poi["phones"][0],
            location_type=location_type,
            latitude=poi["location"]["coordinates"][0],
            longitude=poi["location"]["coordinates"][1],
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
