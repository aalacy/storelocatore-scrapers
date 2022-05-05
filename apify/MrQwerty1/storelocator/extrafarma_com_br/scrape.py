from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID


def fetch_data(sgw: SgWriter):
    api = "https://www.extrafarma.com.br/api/dataentities/LS/search/?_fields=id,Codigo,latitude,longitude,Cidade,endereco,Loja,UF,Telefone,AtendimentoWhatsapp,AtendimentoDiadeSemana,AtendimentoDomingo,AtendimentoFeriado,AtendimentoSabado,24h,Vacina,testesrapidos,testecovid,servicofarmaceutico,rappi,estacionamento,drivethru,delivery,descartometro"
    r = session.get(api, headers=headers)
    js = r.json()

    for j in js:
        street_address = j.get("endereco") or ""
        if street_address.strip() == "-":
            street_address = SgRecord.MISSING

        city = j.get("Cidade") or ""
        if "-" in city:
            city = city.split("-")[0].strip()

        state = j.get("UF")
        postal = j.get("cep")
        country_code = "BR"
        store_number = j.get("Codigo")
        location_name = j.get("Loja")
        phone = j.get("Telefone") or j.get("AtendimentoWhatsapp")
        phone = str(phone)
        if "/" in phone:
            phone = phone.split("/")[0].strip()
        if phone.strip() == "-":
            phone = SgRecord.MISSING
        latitude = j.get("latitude")
        longitude = j.get("longitude")

        _tmp = []
        work_start = j.get("AtendimentoDiadeSemana")
        sat_start = j.get("AtendimentoSabado")
        sun_start = j.get("AtendimentoDomingo") or ""
        if "fechada" in sun_start.lower():
            sun_start = "Closed"

        if work_start:
            _tmp.append(f"Mon-Fri: {work_start}")
        if sat_start:
            _tmp.append(f"Sat: {sat_start}")
        if sun_start:
            _tmp.append(f"Sun: {sun_start}")

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
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.extrafarma.com.br/"
    page_url = "https://www.extrafarma.com.br/nossas-lojas"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:98.0) Gecko/20100101 Firefox/98.0",
        "Accept": "application/json",
        "Referer": "https://www.extrafarma.com.br/nossas-lojas",
        "REST-Range": "resources=0-500",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Connection": "keep-alive",
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
