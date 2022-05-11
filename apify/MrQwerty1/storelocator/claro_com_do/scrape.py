from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    adr1 = adr.street_address_1 or ""
    adr2 = adr.street_address_2 or ""
    street = f"{adr1} {adr2}".strip()
    city = adr.city or SgRecord.MISSING
    postal = adr.postcode or SgRecord.MISSING

    return street, city, postal


def get_states():
    out = dict()
    api = "https://www.claro.com.do/DO_CAC_WSB_Cacs/services/cacsService/obtenerZonaGeo"
    r = session.post(api, headers=headers)
    zonas = r.json()["zonas"]

    for z in zonas:
        _id = str(z.get("zona"))
        state = z.get("descripcion")
        out[_id] = state

    return out


def fetch_data(sgw: SgWriter):
    api = "https://www.claro.com.do/DO_CAC_WSB_Cacs/services/cacsService/obtenerCACSByZona"
    params = get_states()

    for _id, state in params.items():
        json_data = {
            "tipo": "0",
            "zona": _id,
        }
        r = session.post(api, headers=headers, json=json_data)
        js = r.json()["cacs"]

        for j in js:
            raw_address = j.get("direccion")
            street_address, city, postal = get_international(raw_address)
            city = city.replace(".", "").strip()
            country_code = "DO"
            store_number = j.get("idCac")
            location_name = j.get("nombre")
            phone = j.get("telefono")
            latitude = j.get("latitud")
            longitude = j.get("longitud")

            _tmp = []
            hours = j.get("lstHorarios") or []
            for h in hours:
                _tmp.append(h.get("fc_descripcion"))

            hours_of_operation = ";".join(_tmp)

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
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
    locator_domain = "https://www.claro.com.do/"
    page_url = "https://www.claro.com.do/personas/cacs/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:98.0) Gecko/20100101 Firefox/98.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Referer": "https://www.claro.com.do/personas/cacs/",
        "Content-Type": "application/json; charset=utf-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.claro.com.do",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Site": "same-origin",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
