from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://api.smashburger.com/mobilem8-web-service/rest/storeinfo/distance?_=1631577365113&attributes=&disposition=PICKUP&latitude=39.41116&longitude=-104.87308&maxResults=500&radius=20000&radiusUnit=mi&statuses=ACTIVE,TEMP-INACTIVE&tenant=sb-us"
    domain = "smashburger.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    data = session.get(start_url, headers=hdr).json()

    all_locations = data["getStoresResult"]["stores"]
    for poi in all_locations:
        if poi["city"] == "NO WHERE":
            continue

        hoo = []
        days = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
        for day in days:
            opens = poi["storeHours"][0][day]["openTime"]["timeString"].split(",")[0]
            closes = poi["storeHours"][0][day]["closeTime"]["timeString"].split(",")[0]
            hoo.append(f"{day} {opens} - {closes}")
        hoo = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url="https://order.smashburger.com/store-selection",
            location_name=poi["city"],
            street_address=poi["street"],
            city=poi["city"],
            state=poi["state"],
            zip_postal=poi["zipCode"],
            country_code=poi["country"],
            store_number=poi["storeName"],
            phone=poi["phoneNumber"],
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
