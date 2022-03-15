import re
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    post = re.findall(r"\d{5}", line)[-1]
    adr = parse_address(International_Parser(), line, postcode=post)
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()
    city = adr.city
    postal = adr.postcode

    return street_address, city, postal


def fetch_data(sgw: SgWriter):
    api = "https://portail.rexel.fr/-/media/rexel/files/agences.json"
    r = session.get(api, headers=headers)
    js = r.json()["features"]

    for j in js:
        try:
            longitude, latitude = j["geometry"]["coordinates"]
        except:
            longitude, latitude = SgRecord.MISSING, SgRecord.MISSING

        j = j["properties"]
        location_name = j.get("name")
        line = j.get("address") or []
        line = list(filter(None, [l.strip() for l in line]))
        raw_address = ", ".join(line)
        street_address, city, postal = get_international(raw_address)
        store_number = j.get("id")
        slug = j.get("agency_url")
        page_url = f"https://portail.rexel.fr{slug}"
        phone = j.get("phone")

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code="FR",
            phone=phone,
            store_number=store_number,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.rexel.fr/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
    }

    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
