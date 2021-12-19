from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.toyotapr.com/dynamic/data/dealer_tdpr.json"
    domain = "toyotapr.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    all_locations = session.get(start_url, headers=hdr).json()
    for poi in all_locations:
        hoo = []
        for day, hours in poi["salesHours"].items():
            if hours.get("open"):
                opens = hours["open"] // 60
                closes = hours["close"] // 60
                hoo.append(f"{day} {opens} - {closes}")
            else:
                hoo.append(f"{day} closed")
        hoo = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url=poi.get("website"),
            location_name=poi["name"],
            street_address=poi["mailingAddress"]["address1"],
            city=poi["mailingAddress"]["city"],
            state=poi["mailingAddress"]["state"],
            zip_postal=poi["mailingAddress"]["postalCode"],
            country_code="PR",
            store_number="",
            phone=poi["primaryPhone"],
            location_type="",
            latitude=poi["latitude"],
            longitude=poi["longitude"],
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
