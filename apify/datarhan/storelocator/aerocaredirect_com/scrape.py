from sgrequests import SgRequests

from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://api.storerocket.io/api/user/WLy8GYO4r0/locations"
    domain = "aerocaredirect.com"

    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    data = session.get(start_url, headers=hdr).json()

    all_locations = data["results"]["locations"]
    for poi in all_locations:
        store_url = (
            f'https://aerocaredirect.com/pages/store-locator?location={poi["obf_id"]}'
        )
        street_address = poi["display_address"]
        if street_address.endswith(","):
            street_address = street_address[:-1]
        phone = ""
        if poi.get("fields"):
            phone = poi["fields"][0]["pivot_field_value"]
        phone = phone if phone and phone != "() -" else "<MISSING>"

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=poi["name"],
            street_address=street_address,
            city=poi["city"],
            state=poi["state"],
            zip_postal=poi["postcode"],
            country_code=poi["country"],
            store_number=poi["id"],
            phone=phone,
            location_type=poi["locationType"]["name"],
            latitude=poi["lat"],
            longitude=poi["lng"],
            hours_of_operation=SgRecord.MISSING,
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
