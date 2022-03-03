import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
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
    page_url = "https://mcdonalds.com.gt/restaurantes"
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//div[@data-page]/@data-page"))
    js = json.loads(text)["props"]["restaurants"]

    for j in js:
        location_name = j.get("name")
        raw_address = j.get("address")
        street_address, city, state, postal = get_international(raw_address)
        if city:
            if city[-1].isdigit():
                city = "Guatemala"
        if city == "La":
            city = "San Marcos"
        phone = j.get("phone")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        _types = j.get("categorias") or []
        location_type = ", ".join(_types)
        store_number = j.get("id")

        _tmp = []
        hours = j.get("horarios") or []
        if isinstance(hours, dict):
            hours = hours.values()
        for h in hours:
            if h.get("name") == "Restaurante":
                times = h.get("horarios") or []
                for t in times:
                    day = t.get("description")
                    start = t.get("start_time")
                    end = t.get("end_time")
                    _tmp.append(f"{day}: {start}-{end}")
                break

        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="GT",
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    locator_domain = "https://mcdonalds.com.gt/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
