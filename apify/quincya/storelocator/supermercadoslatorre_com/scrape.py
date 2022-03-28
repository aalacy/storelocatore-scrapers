from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    base_link = "https://culturaguatemala.com/2018_backend_la_torre/web/index.php/admin/service/tiendas"

    session = SgRequests()
    stores = session.get(base_link, headers=headers).json()["tiendas"]

    locator_domain = "https://www.supermercadoslatorre.com"

    for store in stores:
        location_name = store["Nombre"]
        city = store["municipio"]
        state = store["departamento"]
        zip_code = ""
        country_code = "Guatemala"
        street_address = (
            store["direccion"]
            .split(", " + city[:5])[0]
            .split(", " + state)[0]
            .split("Sta. Cata")[0]
            .split(", Guatemala")[0]
            .split(", GUAT")[0]
            .replace("Guatemala", "")
            .split(city)[0]
        )
        if street_address[:1] == ",":
            street_address = street_address[1:].strip()
        store_number = store["id"]
        location_type = "<MISSING>"
        phone = store["Telefono"]
        hours_of_operation = store["Hora_apertura"] + "-" + store["Hora_Cierre"]
        latitude = store["Latitud"]
        longitude = store["Longitud"]
        link = "https://www.supermercadoslatorre.com/web/index.php/ubicaciones"

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url=link,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
