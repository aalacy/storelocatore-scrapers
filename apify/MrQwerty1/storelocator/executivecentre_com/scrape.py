from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    adr1 = adr.street_address_1 or ""
    adr2 = adr.street_address_2 or ""
    street = f"{adr1} {adr2}".strip()
    state = adr.state or SgRecord.MISSING
    postal = adr.postcode or SgRecord.MISSING

    return street, state, postal


def fetch_data(sgw: SgWriter):
    api = "https://www.executivecentre.com/page-data/locations/page-data.json"
    r = session.get(api, headers=headers)
    js = r.json()["result"]["data"]["buildings"]["nodes"]

    for j in js:
        location_name = j.get("_name")
        slug = j.get("slug")
        page_url = f"https://www.executivecentre.com/office-space/{slug}"

        a = j.get("_centreJson") or {}
        phone = a.get("phone") or ""
        if "(" in phone:
            phone = phone.split("(")[0].strip()

        raw_address = a.get("address")
        street_address, state, postal = get_international(raw_address)
        city = j["_city"]["name"]
        country_code = j["_country"]["name"]
        store_number = j.get("Id")
        latitude = a.get("map_lat")
        longitude = a.get("map_long")

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            store_number=store_number,
            locator_domain=locator_domain,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.executivecentre.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
