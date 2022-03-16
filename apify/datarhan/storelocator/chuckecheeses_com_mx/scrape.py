from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://chuckecheeses.com.mx/php/sucursalescmp.php"
    domain = "chuckecheeses.com.mx"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    data = session.get(start_url, headers=hdr).json()
    all_locations = data["sucursales"].items()
    for store_number, poi_data in all_locations:
        raw_adr = " ".join(poi_data[0][3].split()).replace("<br>", "")
        addr = parse_address_intl(raw_adr.replace("CDMX", ""))
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += ", " + addr.street_address_2
        zip_code = addr.postcode
        if zip_code:
            zip_code = zip_code.replace(".", "").replace("CP", "").strip()
        city = addr.city
        location_name = poi_data[0][0].replace("<Br>", "").strip()
        if not city:
            city = location_name

        item = SgRecord(
            locator_domain=domain,
            page_url="https://chuckecheeses.com.mx/sucursales.html",
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=addr.state,
            zip_postal=zip_code,
            country_code="MX",
            store_number=store_number,
            phone=poi_data[0][1],
            location_type="",
            latitude=poi_data[0][4],
            longitude=poi_data[0][5],
            hours_of_operation=poi_data[0][2].replace("<br>", "").strip(),
            raw_address=raw_adr,
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
