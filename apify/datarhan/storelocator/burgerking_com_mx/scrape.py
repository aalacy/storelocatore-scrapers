from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    start_url = "https://api-lac.menu.app/api/directory/search"
    domain = "burgerking.com.mx"
    hdr = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "application/json",
        "Accept-Language": "en",
        "Content-Type": "application/json",
        "Content-Language": "en",
        "Device-UUID": "1234",
        "Application": "e6ad9ad7327430cf1f67ec414f730c70",
    }
    frm = {
        "device_uuid": "rista@menu.app",
        "latitude": "19.464815",
        "longitude": "-99.084676",
    }
    data = session.post(start_url, headers=hdr, json=frm).json()

    all_locations = data["data"]["venues"]
    for poi in all_locations:
        street_address = poi["venue"]["address"]
        url_p_1 = (
            street_address.replace("/", " ")
            .replace(",", "")
            .replace(".", "")
            .lower()
            .replace(" ", "-")
            .replace("á", "a")
        )
        store_number = poi["venue"]["id"]
        latitude = poi["venue"]["latitude"]
        longitude = poi["venue"]["longitude"]
        page_url = f"https://www.burgerking.com.mx/restaurantes/{url_p_1}/?id={store_number}&lat={latitude}&lng={longitude}"

        days_dict = {
            1: "Monday",
            2: "Tuesday",
            3: "Wednesday",
            4: "Thursday",
            5: "Friday",
            6: "Saturday",
            0: "Sunday",
        }
        hoo = []
        for e in poi["venue"]["serving_times"]:
            for d in e["days"]:
                day = days_dict[d]
                opens = e["time_from"]
                closes = e["time_to"]
                hoo.append(f"{day} {opens} - {closes}")
        hours_of_operation = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["venue"]["name"],
            street_address=street_address,
            city=poi["venue"]["city"],
            state=SgRecord.MISSING,
            zip_postal=poi["venue"]["zip"],
            country_code=poi["venue"]["country"]["code"],
            store_number=store_number,
            phone=SgRecord.MISSING,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
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
