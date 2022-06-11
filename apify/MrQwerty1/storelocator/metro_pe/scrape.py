import json5
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    adr1 = adr.street_address_1 or ""
    adr2 = adr.street_address_2 or ""
    street = f"{adr1} {adr2}".strip()
    city = adr.city or SgRecord.MISSING
    state = adr.state or SgRecord.MISSING
    postal = adr.postcode or SgRecord.MISSING

    return street, city, state, postal


def fetch_data(sgw: SgWriter):
    api = "https://www.metro.pe/files/mtf.contact.min.js"
    r = session.get(api, headers=headers)
    text = r.text.split("storesJSON:")[1].split(",storeSelector")[0].split("offices:")
    text.pop(0)

    for t in text:
        t = t.split("]},")[0] + "]"
        if t.endswith("}}]"):
            t = t.replace("}}]", "")
        js = json5.loads(t)
        for j in js:
            raw_address = j.get("address")
            street_address, city, state, postal = get_international(raw_address)
            country_code = "PE"
            location_name = j.get("name")
            phone = j.get("phone")
            latitude = j.get("lat")
            longitude = j.get("lng")
            hours_of_operation = ";".join(j.get("schedule") or []).replace("*", "")

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                country_code=country_code,
                latitude=latitude,
                longitude=longitude,
                phone=phone,
                hours_of_operation=hours_of_operation,
                locator_domain=locator_domain,
                raw_address=raw_address,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.metro.pe/"
    page_url = "https://www.metro.pe/institucional/nuestras-tiendas"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_NAME}
            )
        )
    ) as writer:
        fetch_data(writer)
