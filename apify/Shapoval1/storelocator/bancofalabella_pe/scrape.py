from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.bancofalabella.pe/"
    session = SgRequests()
    headers = {
        "Authorization": "Bearer 8874194a80a9396deb8f1034609f4c2186183792232c0af82a73b350ab2ce5af",
    }

    params = (
        ("select", "fields,sys"),
        ("content_type", "sucursal"),
        ("order", "sys.createdAt"),
        ("skip", "0"),
        ("limit", "100"),
        ("include", "5"),
    )

    r = session.get(
        "https://cdn.contentful.com/spaces/jsyhqx93uo07/environments/master/entries",
        headers=headers,
        params=params,
    )
    js = r.json()["items"]
    for j in js:
        b = j.get("fields")
        page_url = "https://www.bancofalabella.pe/sucursales"
        location_name = b.get("name") or "<MISSING>"
        ad = b.get("address") or "<MISSING>"
        a = parse_address(International_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        if postal.find(".") != -1:
            postal = "<MISSING>"
        country_code = "PE"
        city = a.city or "<MISSING>"
        latitude = b.get("coordinates").get("lat")
        longitude = b.get("coordinates").get("lon")
        hours_of_operation = (
            "".join(b.get("horarios")).replace("\n", "").replace("\r", "").strip()
        )
        if hours_of_operation.find("CAJA:") != -1:
            hours_of_operation = hours_of_operation.split("CAJA:")[1].strip()
        if hours_of_operation.find("100%") != -1:
            hours_of_operation = hours_of_operation.split("PLATAFORMA:")[1].strip()
        if hours_of_operation.find("PLATAFORMA:") != -1:
            hours_of_operation = hours_of_operation.split(", ENTREGA")[0].strip()

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
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
            SgRecordID({SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LATITUDE})
        )
    ) as writer:
        fetch_data(writer)
