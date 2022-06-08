from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.toyota.com.ar/api/dealerships"
    domain = "toyota.com.ar"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    all_locations = session.get(start_url, headers=hdr).json()
    for poi in all_locations:
        location_type = " ".join([e["name"] for e in poi["services"]])
        if location_type != "Venta y Accesorios":
            continue
        hoo = " ".join(poi["open_hours"].split())
        hoo = (
            hoo.split("Venta Convencional ")[-1]
            .split("Venta")[0]
            .split("Posventa")[0]
            .strip()
        )
        page_url = poi["url"]
        if page_url and "http" not in page_url:
            page_url = "http://" + page_url
        phones = (
            poi["phone_numbers"]
            .split("Turnos")[0]
            .split("/")[0]
            .replace("(líneas rotativas)", "")
            .replace("(Ventas)", "")
            .strip()
        )
        if phones.endswith("("):
            phones = phones[:-1]

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["name"],
            street_address=poi["address"],
            city=poi["city"],
            state=poi["province"],
            zip_postal="",
            country_code="AR",
            store_number=poi["id"],
            phone=phones,
            location_type=location_type,
            latitude=poi["lat"],
            longitude=poi["lng"],
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
