from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    post = line.split(",")[-1].strip()
    if "A" in post:
        post = post.split("A")[-1].strip()
    adr = parse_address(International_Parser(), line, postcode=post)
    adr1 = adr.street_address_1 or ""
    adr2 = adr.street_address_2 or ""
    street = f"{adr1} {adr2}".strip()
    city = adr.city or SgRecord.MISSING
    postal = adr.postcode or SgRecord.MISSING

    return street, city, postal


def fetch_data(sgw: SgWriter):
    api = "https://stopcafe.pl/wp-content/uploads/ssf-wp-uploads/ssf-data.json"
    r = session.get(api, headers=headers)
    js = r.json()["item"]

    for j in js:
        location_name = j.get("location") or ""
        raw_address = j.get("address")
        street_address, city, postal = get_international(raw_address)
        if city == SgRecord.MISSING:
            city = (
                location_name.split("-")[-1]
                .replace("I", "")
                .replace("ORLEN", "")
                .strip()
            )
        country_code = j.get("country")
        store_number = j.get("storeId")
        phone = j.get("telephone")
        latitude = j.get("latitude")
        longitude = j.get("longitude")

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            store_number=store_number,
            raw_address=raw_address,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://stopcafe.pl/"
    page_url = "https://stopcafe.pl/lokalizacje/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
