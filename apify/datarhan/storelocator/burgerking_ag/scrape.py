from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://api-lac.menu.app/api/directory/search"
    domain = "burgerking.com.ar"
    hdr = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:91.0) Gecko/20100101 Firefox/91.0",
        "Accept": "application/json",
        "Accept-Language": "en",
        "Content-Type": "application/json",
        "Content-Language": "en",
        "Device-UUID": "1234",
        "Application": "burger-king-argentina-lac-prod",
    }
    frm = {
        "latitude": "-34.68467213517914",
        "longitude": "-58.55694354898238",
        "device_uuid": "1234",
    }
    data = session.post(start_url, headers=hdr, json=frm).json()

    all_locations = data["data"]["venues"]
    for poi in all_locations:
        page_url = "https://www.burgerking.com.ar/restaurantes/{}/?id={}&lat={}&lng={}"
        page_url = page_url.format(
            poi["venue"]["address"].replace(",", "").replace(" ", "-").lower(),
            poi["venue"]["id"],
            poi["venue"]["latitude"],
            poi["venue"]["longitude"],
        )
        days = {
            0: "Monday",
            1: "Tuesday",
            2: "Wednesday",
            3: "Thursday",
            4: "Friday",
            5: "Saturday",
            6: "Sunday",
        }
        hoo = []
        for e in poi["venue"]["serving_times"]:
            if not e.get("days"):
                continue
            for d in e["days"]:
                day = days[d]
                opens = e["time_from"]
                closes = e["time_to"]
                hoo.append(f"{day} {opens} - {closes}")
        hoo = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["venue"]["name"],
            street_address=poi["venue"]["address"],
            city=poi["venue"]["city"],
            state=SgRecord.MISSING,
            zip_postal=poi["venue"]["zip"],
            country_code=poi["venue"]["country"]["code"],
            store_number=poi["venue"]["id"],
            phone=poi["venue"]["phone"],
            location_type=SgRecord.MISSING,
            latitude=poi["venue"]["latitude"],
            longitude=poi["venue"]["longitude"],
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
