import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://centros-experiencia-dot-modified-wonder-87620.appspot.com/"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'const LISTA ')]/text()"))
    text = text.split('"')[1].replace("&quot;", '"')
    js = json.loads(text)

    for j in js:
        street_address = j.get("direccion")
        city = j.get("ciudad")
        country_code = "CO"
        store_number = j.get("id")
        location_name = j.get("nombreSucursal")
        location_type = j.get("tipoSucursal")
        phone = j.get("telefono")
        latitude, longitude = str(j.get("coordenada")).split(",")
        hours_of_operation = j.get("horario")

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            store_number=store_number,
            location_type=location_type,
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.movistar.com.co/"
    page_url = "https://www.movistar.com.co/centros-de-experiencia"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
