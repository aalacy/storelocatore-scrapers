import json5
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
    postal = adr.postcode or SgRecord.MISSING

    return street, city, postal


def get_hoo(page_url):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    _tmp = []
    hours = tree.xpath("//table[@class='work-time table']//tr")
    for h in hours:
        day = "".join(h.xpath("./th//text()")).strip()
        inter = "".join(h.xpath("./td//text()")).strip()
        _tmp.append(f"{day}: {inter}")

    return ";".join(_tmp)


def fetch_data(sgw: SgWriter):
    api = "https://cdn.shopify.com/s/files/1/0615/6012/7711/t/2/assets/storeifyapps-geojson.js"
    r = session.get(api, headers=headers)
    source = r.text.replace("eqfeed_callback(", "").replace(");", "")
    js = json5.loads(source)["features"]

    for j in js:
        p = j.get("properties") or {}
        location_type = p.get("category")
        raw_address = p.get("address")
        street_address, city, postal = get_international(raw_address)
        country_code = "US"
        store_number = p.get("id")
        location_name = p.get("name")
        slug = p.get("url")
        page_url = f"https://www.vanity.com.mx{slug}"
        phone = p.get("phone")
        latitude = p.get("lat")
        longitude = p.get("lng")
        hours_of_operation = get_hoo(page_url)

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
            location_type=location_type,
            raw_address=raw_address,
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.vanity.com.mx/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
