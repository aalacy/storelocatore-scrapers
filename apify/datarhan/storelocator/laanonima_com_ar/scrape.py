# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = (
        "https://www.laanonima.com.ar/contents/themes/responsive/bin/get_sucursales.php"
    )
    domain = "laanonima.com.ar"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    all_locations = session.get(start_url, headers=hdr).json()
    for poi in all_locations:
        raw_address = poi["direccion"]
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        hoo = f'Lunes a Viernes: {poi["h_lv"]}, Sábado: {poi["h_sab"]}, Domingo: {poi["h_dom"]}'
        city = addr.city
        if city and city.endswith("."):
            city = city[:-1]
        state = addr.state
        if state and state.endswith("."):
            state = state[:-1]
        phone = poi["telefono"].replace(" ? ", "-").split("/")[0]
        if phone and len(phone) > 16:
            phone = phone.split(" - ")[0]

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.laanonima.com.ar/" + poi["url"],
            location_name=poi["nombre"],
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=addr.postcode,
            country_code="AR",
            store_number=poi["sucursal"],
            phone=phone,
            location_type="",
            latitude=poi["lat"],
            longitude=poi["lng"],
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
