import json5
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()
    city = adr.city or ""
    state = adr.state
    postal = adr.postcode or ""

    return street_address, city, state, postal


def get_coords_from_embed(text):
    try:
        latitude = text.split("!3d")[1].strip().split("!")[0].strip()
        longitude = text.split("!2d")[1].strip().split("!")[0].strip()
    except IndexError:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    return latitude, longitude


def fetch_data(sgw: SgWriter):
    api = "http://www.vitrocar.com.mx/scripts/mapa.js"
    r = session.get(api)
    text = r.text.split("var list = ")[1].split("var estadoSelect")[0].replace(";", "")
    js = json5.loads(text)["vitrocar"]

    for jj in js:
        for j in jj["sucursales"]:
            location_name = j.get("nombre")
            raw_address = j.get("direccion")
            street_address, city, state, postal = get_international(raw_address)
            if city == "":
                city = location_name
            postal = "".join(postal.split()).replace("C.P.", "").strip()
            if postal == "" and "C.P." in "".join(raw_address.split()):
                postal = "".join(raw_address.split()).split("C.P.")[-1].strip()
            phone = j.get("telefono1")
            source = j.get("link")
            latitude, longitude = get_coords_from_embed(source)

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code="MX",
                phone=phone,
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                raw_address=raw_address,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "http://www.vitrocar.com.mx/"
    page_url = "http://www.vitrocar.com.mx/sucursales"
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.RAW_ADDRESS, SgRecord.Headers.LOCATION_NAME})
        )
    ) as writer:
        fetch_data(writer)
