from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://www.toyotarp.com/components/com_sucursales/assets/json/sucursales_v5.json?a=20.2"
    domain = "toyotarp.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    data = session.get(start_url, headers=hdr).json()
    for poi in data["sucursales"]:
        location_type = ", ".join([e["desc"] for e in poi["servicios"]])
        geo = poi["pocision"].split(",")
        hoo = ", ".join(poi["horario"])
        raw_address = poi["direccion"].replace(";", ",")
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += ", " + addr.street_address_2
        if street_address and street_address.endswith(","):
            street_address = street_address[:-1]

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.toyotarp.com/sucursales",
            location_name=poi["nombre"],
            street_address=street_address,
            city=addr.city,
            state=addr.state,
            zip_postal=addr.postcode,
            country_code="Panama",
            store_number=poi["suc_id"],
            phone=poi["tel"][0],
            location_type=location_type,
            latitude=geo[0],
            longitude=geo[1],
            hours_of_operation=hoo,
            raw_address=raw_address,
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
