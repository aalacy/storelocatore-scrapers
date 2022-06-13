from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.belmo.com.ar/"
    api_url = "https://www.belmo.com.ar/api/dataentities/SU/search?an=simmonsarg&_fields=id,activa,ciudad,codigopostal,direccion,email,horario,imagen,latitud,longitud,nombre,provincia,retiro,telefono,simmons,simmonsStore,belmo,yolo&_sort=nombre+ASC"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://www.belmo.com.ar/sucursales",
        "rest-range": "resources=0-250",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Connection": "keep-alive",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:

        page_url = "https://www.belmo.com.ar/sucursales"
        location_name = j.get("nombre") or "<MISSING>"
        tmp = []
        simmons = j.get("simmons")
        if simmons:
            tmp.append("simons")
        belmo = j.get("belmo")
        if belmo:
            tmp.append("belmo")
        simmonsStore = j.get("simmonsStore")
        if simmonsStore:
            tmp.append("simmonsStore")
        location_type = ", ".join(tmp) or "<MISSING>"
        street_address = j.get("direccion") or "<MISSING>"
        ad = "".join(j.get("ciudad"))
        country_code = "AR"
        city = ad
        if city.find(",") != -1:
            city = city.split(",")[-1].strip()
        latitude = j.get("latitud") or "<MISSING>"
        longitude = j.get("longitud") or "<MISSING>"
        latitude = str(latitude).replace(",", ".").strip()
        longitude = str(longitude).replace(",", ".").strip()
        phone = j.get("telefono") or "<MISSING>"
        phone = str(phone).replace("Fijo:", "").strip()
        if str(phone).find("/") != -1:
            phone = str(phone).split("/")[0].strip()
        if str(phone).find("|") != -1:
            phone = str(phone).split("|")[0].strip()
        hours_of_operation = j.get("horario") or "<MISSING>"

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
            zip_postal=SgRecord.MISSING,
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
                {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_NAME}
            )
        )
    ) as writer:
        fetch_data(writer)
