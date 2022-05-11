from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.bancofalabella.cl/"
    page_url = "https://www.bancofalabella.cl/oficinas"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "X-Contentful-User-Agent": "sdk contentful.js/0.0.0-determined-by-semantic-release; platform browser; os Linux;",
        "Authorization": "Bearer 560c0ddde9630e43122ef3e7879d69013844ee3d48c566d4ba93125924f080dd",
        "Origin": "https://www.bancofalabella.cl",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
    }

    params = {
        "select": "fields,sys.id,sys.type",
        "content_type": "sucursal",
        "limit": "300",
    }

    r = session.get(
        "https://cntn.bancofalabella.cl/spaces/p6eyia4djstu/environments/master/entries",
        headers=headers,
        params=params,
    )
    js = r.json()["items"]
    for j in js:
        a = j.get("fields")
        location_name = a.get("name")
        location_type = a.get("brand")
        ad = a.get("address")
        b = parse_address(International_Parser(), ad)
        street_address = (
            f"{b.street_address_1} {b.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        if street_address == "<MISSING>" or street_address.isdigit():
            street_address = ad
        state = b.state or "<MISSING>"
        postal = b.postcode or "<MISSING>"
        country_code = "CL"
        city = b.city or "<MISSING>"
        latitude = a.get("coordinates").get("lat")
        longitude = a.get("coordinates").get("lon")
        hours_of_operation = "".join(a.get("horarios")).replace("\n", " ").strip()
        if hours_of_operation.find("Cerrado,") != -1:
            hours_of_operation = hours_of_operation.split(",")[0].strip()
        if hours_of_operation.find("Los días") != -1:
            hours_of_operation = hours_of_operation.split("Los días")[0].strip()
        if hours_of_operation.find("Cerrado temporalmente,") != -1:
            hours_of_operation = hours_of_operation.split(",")[0].strip()
        if (
            hours_of_operation.find("Cerrado/") != -1
            or hours_of_operation.find("Cerrado por remodelaciones /") != -1
        ):
            hours_of_operation = hours_of_operation.split("/")[0].strip()

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
            location_type=location_type,
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
            SgRecordID({SgRecord.Headers.RAW_ADDRESS, SgRecord.Headers.LATITUDE})
        )
    ) as writer:
        fetch_data(writer)
