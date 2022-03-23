from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://chedraui.com.mx/"
    api_url = "https://omni.chedraui.com.mx/api-ubicaciones/public/api/ubicaciones"
    session = SgRequests(verify_ssl=False)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["ubicaciones"]
    for j in js:

        page_url = "https://www.chedraui.com.mx/ubicacion-de-tiendas"
        location_name = j.get("nombre") or "<MISSING>"
        ad = j.get("direccion")
        a = parse_address(International_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        state = j.get("estado")
        postal = a.postcode or "<MISSING>"
        postal = (
            str(postal)
            .replace(".", "")
            .replace("C", "")
            .replace("P", "")
            .replace("ENTRE", "")
            .replace("ESTADO", "")
            .strip()
            or "<MISSING>"
        )
        country_code = "MX"
        city = a.city or "<MISSING>"
        if city == "<MISSING>":
            city = state
        store_number = j.get("id_tienda") or "<MISSING>"
        latitude = j.get("latitud") or "<MISSING>"
        longitude = j.get("longitud") or "<MISSING>"
        hours_of_operation = (
            f"{j.get('horario_apertura')} - {j.get('horario_cierre')}".strip()
            or "<MISSING>"
        )
        location_type = j.get("formato_tienda")

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=SgRecord.MISSING,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
