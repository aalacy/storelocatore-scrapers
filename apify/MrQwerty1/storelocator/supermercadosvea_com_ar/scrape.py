import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID


def fetch_data(sgw: SgWriter):
    api = "https://supermercadosvea.com.ar/caba/sucursales/"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(
        tree.xpath("//script[contains(text(), 'var sucursalesData = ')]/text()")
    )
    text = text.split("var sucursalesData = ")[1].strip()[:-1]
    js = json.loads(text)

    for j in js:
        street_address = j.get("direccion")
        city = j.get("city")
        state = j.get("province")
        country_code = "AR"
        location_name = j.get("nombre")
        phone = j.get("telefono")
        latitude = j.get("latitud")
        longitude = j.get("longitud")
        slug = j.get("cluster") or ""
        page_url = f"https://supermercadosvea.com.ar/{slug}/sucursales/"
        hours_of_operation = j.get("horario") or ""
        hours_of_operation = (
            hours_of_operation.replace("\n", "")
            .replace("\r", "")
            .replace("<br />", ";")
            .replace("</br>", ";")
        )

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://supermercadosvea.com.ar/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_NAME}
            )
        )
    ) as writer:
        fetch_data(writer)
