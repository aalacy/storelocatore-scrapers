from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.pichincha.pe/"
    api_url = (
        "https://www.pichincha.pe/lugaresdepago/path---index-fc3edc7dfc99c1ff0732.js"
    )
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    div = r.text.split("spots:{edges:")[1].split(");")[0].strip()
    block = div.split("node")[1:]
    for b in block:

        page_url = "https://www.pichincha.pe/servicio-al-cliente/nuestras-agencias"
        location_name = b.split('name:"')[1].split('"')[0].strip()
        location_type = b.split('type:"')[1].split('"')[0].strip()
        street_address = b.split('direction:"')[1].split('"')[0].strip()
        state_id = b.split('stateId:"')[1].split('"')[0].strip()
        state = r.text.split(f"{state_id}")[1].split('name:"')[1].split('"')[0].strip()
        country_code = "PE"
        city_id = b.split('districtId:"')[1].split('"')[0].strip()
        city = r.text.split(f"{city_id}")[1].split('name:"')[1].split('"')[0].strip()
        latitude = b.split('latitude:"')[1].split('"')[0].strip()
        longitude = b.split('longitude:"')[1].split('"')[0].strip()
        hours_of_operation = (
            b.split('horarioNormal:"')[1].split('"')[0].strip()
            + " Sabado "
            + b.split('sabado:"')[1].split('"')[0].strip()
        )
        hours_of_operation = hours_of_operation.strip() or "<MISSING>"
        if hours_of_operation == "Sabado":
            hours_of_operation = "<MISSING>"

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=SgRecord.MISSING,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=SgRecord.MISSING,
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
                    SgRecord.Headers.LOCATION_TYPE,
                }
            )
        )
    ) as writer:
        fetch_data(writer)
