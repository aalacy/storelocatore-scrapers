from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.brooksbrothers.mx"
urls = {
    "mall": "https://www.brooksbrothers.mx/api/dataentities/TI/search?_where=tipo=*Mall*&_fields=id,id_tienda,nombre_sucursal,ciudad,estado,direccion,colonia,cp,latitud,longitud,phone,horario&_sort=nombre_sucursal",
    "outlet": "https://www.brooksbrothers.mx/api/dataentities/TI/search?_where=tipo=*Outlet*&_fields=id,id_tienda,nombre_sucursal,ciudad,estado,direccion,colonia,cp,latitud,longitud,phone,horario&_sort=nombre_sucursal",
}


def fetch_data():
    with SgRequests() as session:
        for location_type, base_url in urls.items():
            locations = session.get(base_url, headers=_headers).json()
            for _ in locations:
                yield SgRecord(
                    page_url="https://www.brooksbrothers.mx/localiza-tu-tienda",
                    store_number=_["id_tienda"],
                    location_name=_["nombre_sucursal"],
                    street_address=_["direccion"],
                    city=_["ciudad"],
                    state=_["estado"],
                    zip_postal=_["cp"],
                    latitude=_["latitud"],
                    longitude=_["longitud"],
                    country_code="MX",
                    location_type=location_type,
                    phone=_["phone"],
                    locator_domain=locator_domain,
                    hours_of_operation=_["horario"].split("Horario especial")[0],
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
