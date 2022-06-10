from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.simmons.com.ar"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "application/vnd.vtex.ds.v10+json",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/json",
        "REST-Range": "resources=0-250",
        "X-Requested-With": "XMLHttpRequest",
        "Connection": "keep-alive",
        "Referer": "https://www.simmons.com.ar/sucursales",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Cache-Control": "max-age=0",
    }

    r = session.get(
        "https://www.simmons.com.ar/api/dataentities/SU/search?_fields=id,activa,ciudad,codigopostal,direccion,email,horario,imagen,latitud,longitud,nombre,provincia,retiro,telefono,simmons,simmonsStore,belmo&_sort=nombre+ASC",
        headers=headers,
    )
    js = r.json()
    for j in js:

        page_url = "https://www.simmons.com.ar/sucursales"
        location_name = j.get("nombre") or "<MISSING>"
        tmp = []
        simmons = j.get("simmons")
        if simmons:
            tmp.append("simmons")
        belmo = j.get("belmo")
        if belmo:
            tmp.append("belmon")
        location_type = ", ".join(tmp) or "<MISSING>"
        street_address = j.get("direccion") or "<MISSING>"
        state = j.get("provincia") or "<MISSING>"
        postal = j.get("codigopostal") or "<MISSING>"
        country_code = "AR"
        city = j.get("ciudad") or "<MISSING>"
        if str(city).find(",") != -1:
            state = str(city).split(",")[1].strip()
            city = str(city).split(",")[0].strip()
        latitude = "".join(j.get("latitud")).replace(",", ".") or "<MISSING>"
        longitude = "".join(j.get("longitud")).replace(",", ".") or "<MISSING>"
        phone = j.get("telefono") or "<MISSING>"
        if str(phone).find("/") != -1:
            phone = str(phone).split("/")[0].strip()
        if str(phone).find("|") != -1:
            phone = str(phone).split("|")[0].replace("Fijo: ", "").strip()
        hours_of_operation = j.get("horario") or "<MISSING>"

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.LATITUDE,
                }
            )
        )
    ) as writer:
        fetch_data(writer)
