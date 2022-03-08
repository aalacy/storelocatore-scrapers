from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.bancognb.com.pe/"
    api_url = "https://www.bancognb.com.pe/web/data/peru/cajeros/lima.json"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:
        location_type = j
        for j in js[f"{location_type}"]:
            page_url = "https://www.bancognb.com.pe/main/oficinas"
            location_name = j.get("nombre") or "<MISSING>"
            street_address = j.get("direccion") or "<MISSING>"
            state = j.get("provincia") or "<MISSING>"
            country_code = "PE"
            city = j.get("distrito") or "<MISSING>"
            latitude = j.get("latitud") or "<MISSING>"
            longitude = j.get("longitud") or "<MISSING>"

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
                hours_of_operation=SgRecord.MISSING,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LOCATION_TYPE,
                }
            )
        )
    ) as writer:
        fetch_data(writer)
