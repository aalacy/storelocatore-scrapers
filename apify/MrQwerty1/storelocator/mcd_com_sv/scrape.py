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
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()
    city = adr.city or ""
    state = adr.state
    postal = adr.postcode

    return street_address, city, state, postal


def fetch_data(sgw: SgWriter):
    page_url = "https://mcdonalds.com.sv/restaurantes"
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//div[@data-page]/@data-page"))
    js = json.loads(text)["props"]["restaurants"]

    for j in js:
        location_name = j.get("name")
        raw_address = j.get("address")
        street_address, city, state, postal = get_international(raw_address)
        phone = j.get("phone")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        cats = j.get("categorias") or []
        if not cats:
            for c in j["horarios"]:
                cats.append(c["name"])

        store_number = j.get("id")

        _tmp = []
        try:
            hours = j["horarios"][0]["horarios"]
        except:
            hours = j["horarios"]["0"]["horarios"]

        for h in hours:
            day = h.get("description")
            start = h.get("start_time")
            end = h.get("end_time")
            _tmp.append(f"{day}: {start}-{end}")

        hours_of_operation = ";".join(_tmp)
        location_type = ",".join(cats)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="SG",
            location_type=location_type,
            store_number=store_number,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://mcdonalds.com.sv/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Accept": "*/*",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
