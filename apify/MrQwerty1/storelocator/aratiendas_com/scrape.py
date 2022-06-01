from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    post = line.split(", ")[-1].split()[0]
    adr = parse_address(International_Parser(), line, postcode=post)
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()
    city = adr.city
    state = adr.state
    postal = adr.postcode

    return street_address, city, state, postal


def fetch_data(sgw: SgWriter):
    r = session.get("https://aratiendas.com/wp-json/map-ara/v1/stores", headers=headers)
    js = r.json()

    for j in js:
        location_name = j.get("name")
        latitude = j.get("latitude") or ""
        longitude = j.get("longitude") or ""
        if str(latitude) == "0" or str(longitude) == "0":
            latitude, longitude = SgRecord.MISSING, SgRecord.MISSING
        phone = j.get("phone")
        store_number = j.get("ID")
        street_address = j.get("address") or ""
        street_address = street_address.replace("\n", ", ")
        city = j.get("city")
        state = j.get("zone")

        _tmp = []
        ms = j.get("schedule_monday_saturday")
        s = j.get("schedule_sunday_festive")
        if ms:
            _tmp.append(f"Monday-Saturday: {ms}")
        if s:
            _tmp.append(f"Sunday: {s}")
        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            country_code="CO",
            phone=phone,
            store_number=store_number,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://aratiendas.com/"
    page_url = "https://aratiendas.com/ubicacion-tiendas/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
    }

    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
