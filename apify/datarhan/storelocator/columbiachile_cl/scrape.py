from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.columbiachile.cl/files/locales.json"
    domain = "columbiachile.cl"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    all_locations = session.get(start_url, headers=hdr).json()
    for poi in all_locations:
        street_address = poi["address"]["street"] + ", " + poi["address"]["number"]

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.columbiachile.cl/tiendas",
            location_name=poi["name"],
            street_address=street_address,
            city=poi["address"]["city"],
            state=poi["address"]["state"],
            zip_postal=poi["address"]["postalCode"],
            country_code=poi["address"]["country"]["name"],
            store_number=poi["id"],
            phone="",
            location_type="",
            latitude=poi["address"]["location"]["latitude"],
            longitude=poi["address"]["location"]["longitude"],
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
