from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    r = session.get(
        "https://www.calvinklein.mx/api/dataentities/TI/search",
        headers=headers,
        params=params,
    )

    for j in r.json():
        location_name = j.get("nombre_sucursal") or ""
        if "CALVIN" not in location_name:
            continue

        row = SgRecord(
            page_url="https://www.calvinklein.mx/ubicacion-de-tiendas",
            location_name=location_name,
            street_address=str(j.get("direccion")).replace("\xa0", " "),
            city=j.get("ciudad"),
            state=j.get("estado"),
            zip_postal=j.get("cp"),
            country_code="MX",
            phone=j.get("phone"),
            latitude=j.get("latitud"),
            longitude=j.get("longitud"),
            store_number=j.get("id_tienda"),
            locator_domain=locator_domain,
            hours_of_operation=j.get("horario"),
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.calvinklein.mx/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0",
        "Accept": "*/*",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Content-Type": "application/json; charset=utf-8",
        "REST-Range": "resources=0-200",
        "Connection": "keep-alive",
        "Referer": "https://www.calvinklein.mx/ubicacion-de-tiendas",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers",
    }

    params = (
        (
            "_fields",
            "id_tienda,phone,nombre_sucursal,ciudad,estado,direccion,colonia,cp,latitud,longitud,telefono,horario",
        ),
        ("_sort", "nombre_sucursal"),
    )
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
