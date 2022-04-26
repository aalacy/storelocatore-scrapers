import json
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


def fetch_data(sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'var pins =')]/text()"))

    _types = dict()
    ttext = text.split("options:")[1].split("}},")[0] + "}}"
    tt = json.loads(ttext).values()
    for t in tt:
        key = t.get("id")
        val = t.get("name")
        _types[key] = val

    text = text.split("var pins =")[1].split("}};")[0] + "}}"
    js = json.loads(text).values()

    for j in js:
        location_name = raw_address = j.get("name")
        _tmp = []
        types = j.get("poi_types") or []
        for _t in types:
            _tmp.append(_types.get(_t))
        location_type = ", ".join(_tmp)
        store_number = j.get("id")
        street_address, city, postal = get_international(raw_address)
        country_code = "GE"
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
            store_number=store_number,
            raw_address=raw_address,
            location_type=location_type,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://gulf.ge/"
    page_url = "https://gulf.ge/en/map"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
