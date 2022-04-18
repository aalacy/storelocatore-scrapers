from lxml import html
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
    state = adr.state or SgRecord.MISSING
    postal = adr.postcode or SgRecord.MISSING

    return street, city, state, postal


def fetch_data(sgw: SgWriter):
    api = "https://j1r8ghsqw8.execute-api.us-east-1.amazonaws.com/pro/api/stores/list"
    json_data = {"language": "es"}
    r = session.post(api, headers=headers, json=json_data)
    js = r.json()["data"]

    for j in js:
        raw_address = j.get("address")
        street_address, city, state, postal = get_international(raw_address)
        country_code = "PE"
        store_number = j.get("storeCode")
        location_name = j.get("storeName")
        phone = j.get("phone")
        latitude = j.get("latitude")
        longitude = j.get("longtitude")
        source = j.get("description") or "<html>"
        tree = html.fromstring(source)
        hours_of_operation = ";".join(tree.xpath("//p/text()"))

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
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://rokys.com/"
    page_url = "https://rokys.com/locales"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:99.0) Gecko/20100101 Firefox/99.0",
        "Accept": "application/json, text/plain, */*",
        "x-api-key": "rEhcO2wDBVaWzonDR6tgx8PPs2qtwaVf6y1GUCr1",
        "Content-Type": "application/json;charset=utf-8",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
