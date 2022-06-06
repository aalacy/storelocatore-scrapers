from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.claro.com.co/CO_CACS_WSB_CentrosClaro/services/cacsServices/obtenerCACSByHorario"
    json_data = 2
    r = session.post(api, headers=headers, json=json_data)
    js = r.json()["cacs"]

    for j in js:
        raw_address = j.get("direccion")
        street_address = raw_address
        country_code = "CO"
        store_number = j.get("idCac")
        location_name = j.get("nombre")
        phone = j.get("telefono")
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
            phone=phone,
            store_number=store_number,
            locator_domain=locator_domain,
            raw_address=raw_address,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.claro.com.co/"
    page_url = "https://www.claro.com.co/personas/cavs/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:98.0) Gecko/20100101 Firefox/98.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Content-Type": "application/json; charset=utf-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.claro.com.co",
        "Connection": "keep-alive",
        "Referer": "https://www.claro.com.co/personas/cavs/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
