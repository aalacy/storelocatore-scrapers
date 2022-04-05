from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.bancofalabella.com.co/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "X-Contentful-User-Agent": "sdk contentful.js/0.0.0-determined-by-semantic-release; platform browser; os Linux;",
        "Authorization": "Bearer d45020a30007d90d7d545eea26de90432d5aaee1ed676c6e0218b2c037d3e6c1",
    }

    params = {
        "select": "fields,sys",
        "content_type": "sucursal",
        "include": "2",
    }

    r = session.get(
        "https://cdn.contentful.com/spaces/ex6ts2p2j0ib/environments/master/entries",
        headers=headers,
        params=params,
    )
    js = r.json()["items"]
    for j in js:

        page_url = "https://www.bancofalabella.com.co/oficinas"
        location_name = j.get("fields").get("name")
        ad = j.get("fields").get("address")
        a = parse_address(International_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "CO"
        city = a.city or "<MISSING>"
        latitude = j.get("fields").get("coordinates").get("lat")
        longitude = j.get("fields").get("coordinates").get("lon")
        hours_of_operation = (
            str(j.get("fields").get("horarios")).replace("\n", " ").strip()
        )
        hours_of_operation = (
            " ".join(hours_of_operation.split()).replace("None", "").strip()
            or "<MISSING>"
        )

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
            SgRecordID(
                {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_NAME}
            )
        )
    ) as writer:
        fetch_data(writer)
