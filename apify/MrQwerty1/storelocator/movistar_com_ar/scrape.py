import httpx
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.movistar.com.ar/ayuda/locales-movistar?p_p_id=portlet_geolocalizadormerlin_WAR_portlet_geolocalizador&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_resource_id=buscarSucursalesPorTipoDeCentro&p_p_cacheability=cacheLevelPage&idTipoCentro=21&idTipoCentro=1&idTipoCentro=61"
    r = httpx.get(api, headers=headers)
    js = r.json()["sucursales"]

    for j in js:
        street_address = j.get("direccion")
        country_code = "AR"
        store_number = j.get("id")
        location_name = j.get("nombre")
        latitude = j.get("latitud")
        longitude = j.get("longitud")
        hours_of_operation = j.get("horario")

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            store_number=store_number,
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.movistar.com.ar/"
    page_url = "https://www.movistar.com.ar/ayuda/locales-movistar"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    httpx._config.DEFAULT_CIPHERS += ":ALL:@SECLEVEL=1"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
