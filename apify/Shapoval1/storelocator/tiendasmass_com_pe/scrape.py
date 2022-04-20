import json
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.tiendasmass.com.pe/"
    api_url = "https://www.tiendasmass.com.pe/js/app.d237d90f.js"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    div = r.text.split("exports=JSON.parse('")[1].split("')},3369")[0].strip()
    js = json.loads(div)

    for j in js:

        page_url = "https://www.tiendasmass.com.pe/nuestros-locales"
        location_name = j.get("name") or "<MISSING>"
        ad = j.get("address") or "<MISSING>"
        a = parse_address(International_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        if street_address == "<MISSING>" or street_address.isdigit():
            street_address = ad
        state_id = j.get("department_id")
        state = (
            r.text.split("e.exports=JSON.parse(")[2]
            .split(f'{state_id},"name":"')[1]
            .split('"')[0]
            .strip()
        )
        country_code = "PE"
        city = j.get("district").get("name") or "<MISSING>"
        store_number = j.get("id") or "<MISSING>"
        latitude = j.get("latitud") or "<MISSING>"
        longitude = j.get("longitud") or "<MISSING>"
        hours_of_operation = (
            "De lunes " + r.text.split('"De lunes')[1].split('")')[0].strip()
        )

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=SgRecord.MISSING,
            country_code=country_code,
            store_number=store_number,
            phone=SgRecord.MISSING,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.LATITUDE})
        )
    ) as writer:
        fetch_data(writer)
