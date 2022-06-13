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
    city = adr.city or SgRecord.MISSING
    postal = adr.postcode or SgRecord.MISSING

    return street, city, postal


def fetch_data(sgw: SgWriter):
    api = "https://apps.elfsight.com/p/boot/?w=d2aec972-31b0-4023-9799-78434e3d926c"
    r = session.get(api, headers=headers)
    js = list(r.json()["data"]["widgets"].values())[0]["data"]["settings"]["markers"]

    for j in js:
        raw_address = j.get("infoAddress") or ""
        location_name = j.get("infoTitle") or ""
        if location_name in raw_address:
            raw_address = raw_address.replace(location_name, "").strip()
        street_address, city, postal = get_international(raw_address)
        country_code = "GB"
        phone = j.get("infoPhone")

        text = j.get("coordinates") or ""
        try:
            latitude, longitude = text.split(", ")
        except:
            latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

        hours_of_operation = j.get("infoWorkingHours") or ""
        hours_of_operation = hours_of_operation.replace(" / ", ";")

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
            raw_address=raw_address,
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.cartridgeworld.co.uk/"
    page_url = "https://www.cartridgeworld.co.uk/our-shops/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
