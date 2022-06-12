from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()
    city = adr.city or ""
    state = SgRecord.MISSING
    postal = adr.postcode

    return street_address, city, state, postal


def fetch_data(sgw: SgWriter):
    api = (
        "https://storemapper-herokuapp-com.global.ssl.fastly.net/api/users/8586/stores"
    )
    r = session.get(api)
    js = r.json()["stores"]

    for j in js:
        location_name = j.get("name")
        page_url = j.get("url")
        phone = j.get("phone")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        hours_of_operation = j.get("custom_field_1") or ""
        hours_of_operation = hours_of_operation.replace("pm ", "pm;")
        raw_address = j.get("address")
        street_address, city, state, postal = get_international(raw_address)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="GB",
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.petsandfriends.co.uk/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
