from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.drogariaspacheco.com.br/api/dataentities/PR/documents/fad9798f-9914-11ea-8337-122b0ab818b1/arquivo/attachments/nossas-lojas.js"
    r = session.get(api, headers=headers)
    js = r.json()["retorno"]

    for j in js:
        street_address = j.get("endereco")
        city = j.get("cidade")
        state = j.get("bairro")
        postal = j.get("cep")
        country_code = "BR"
        store_number = j.get("codigo")
        location_name = j.get("nome")
        phone = j.get("telefoneUm")
        latitude = j.get("latitude")
        longitude = j.get("longitude")

        _tmp = []
        work_start = j.get("horarioAberturaSegsex")
        work_end = j.get("horarioFechamentoSegsex")
        sat_start = j.get("horarioAberturaSabado")
        sat_end = j.get("horarioFechamentoSabado")
        sun_start = j.get("horarioAberturaDomingo")
        sun_end = j.get("horarioFechamentoDomingo")

        if work_start:
            _tmp.append(f"Mon-Fri: {work_start}:{work_end}")
        if sat_start:
            _tmp.append(f"Sat: {sat_start}-{sat_end}")
        if sun_start:
            _tmp.append(f"Sun: {sun_start}-{sun_end}")

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
    locator_domain = "https://www.drogariasaopaulo.com.br/"
    page_url = "https://www.drogariasaopaulo.com.br/institucional/nossas-lojas"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
