from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://unnuevobancojuntos.pe/"
    api_url = (
        "https://unnuevobancojuntos.pe/mapademo/get-agencia.php?accion=get_departamento"
    )
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:
        depart = j
        sub_page_url = f"https://unnuevobancojuntos.pe/mapademo/get-agencia.php?accion=get_provincia&departamento={depart}"
        r = session.get(sub_page_url, headers=headers)
        js = r.json()
        for j in js:
            province = j
            ssub_page_url = f"https://unnuevobancojuntos.pe/mapademo/get-agencia.php?accion=get_distrito&departamento={depart}&provincia={province}"
            r = session.get(ssub_page_url, headers=headers)
            js = r.json()
            for j in js:
                distrito = j
                api_url = f"https://unnuevobancojuntos.pe/mapademo/get-agencia.php?accion=get_sucursal&departamento={depart}&provincia={province}&distrito={distrito}"
                r = session.get(api_url, headers=headers)
                js = r.json()
                for j in js.values():

                    page_url = "https://www.alfinbanco.pe/agencias"
                    street_address = j.get("direccion") or "<MISSING>"
                    state = j.get("provincia") or "<MISSING>"
                    country_code = "PE"
                    city = "".join(j.get("distrito")).strip() or "<MISSING>"
                    latitude = j.get("lat") or "<MISSING>"
                    longitude = j.get("lng") or "<MISSING>"

                    row = SgRecord(
                        locator_domain=locator_domain,
                        page_url=page_url,
                        location_name=SgRecord.MISSING,
                        street_address=street_address,
                        city=city,
                        state=state,
                        zip_postal=SgRecord.MISSING,
                        country_code=country_code,
                        store_number=SgRecord.MISSING,
                        phone=SgRecord.MISSING,
                        location_type=SgRecord.MISSING,
                        latitude=latitude,
                        longitude=longitude,
                        hours_of_operation=SgRecord.MISSING,
                    )

                    sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LATITUDE})
        )
    ) as writer:
        fetch_data(writer)
