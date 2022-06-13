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
    page_url = "https://www.esteler77.com/outlet"
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'var locations')]/text()"))
    text = text.split("var latlngs =")[1].split("}];")[0] + "}]"
    js = json.loads(text)

    for j in js:
        location_name = j.get("place_name")
        phone = j.get("phone")
        ll = j.get("latlang") or ","
        latitude = ll.split(",")[0].strip()
        longitude = ll.split(",")[1].strip()
        hours_of_operation = j.get("open_hours")
        store_number = j.get("id")
        source = j.get("address") or "<html></html>"
        root = html.fromstring(source)
        raw = root.xpath("//text()")
        raw = list(filter(None, [ra.strip() for ra in raw]))
        raw_address = " ".join(raw)
        street_address, city, state, postal = get_international(raw_address)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="ID",
            phone=phone,
            store_number=store_number,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.esteler77.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
