from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "carliecs.com"
    start_url = "https://api.freshop.com/1/stores?app_key=carlie_c_s&has_address=true&limit=-1&token={}"

    frm = {
        "app_key": "carlie_c_s",
        "referrer": "https://www.carliecs.com/",
        "utc": "1626174932446",
    }
    token = session.post("https://api.freshop.com/2/sessions/create", data=frm).json()
    data = session.get(start_url.format(token["token"])).json()

    for poi in data["items"]:
        page_url = poi.get("url")
        if not page_url:
            page_url = "https://www.carliecs.com/my-store/store-locator"

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["name"],
            street_address=poi["address_1"],
            city=poi["city"],
            state=poi["state"],
            zip_postal=poi["postal_code"],
            country_code="",
            store_number=poi["number"],
            phone=poi["phone_md"].split("\n")[0].strip(),
            location_type="",
            latitude=poi["latitude"],
            longitude=poi["longitude"],
            hours_of_operation=poi["hours_md"]
            .replace("\n", " ")
            .split("Senior")[0]
            .strip(),
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
