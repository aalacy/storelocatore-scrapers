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
    page_url = "https://www.decathlon.my/content/14-prodavnice"
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    text = "".join(
        tree.xpath("//script[contains(text(), 'store_marker.push(')]/text()")
    ).split("store_marker.push(")

    for t in text:
        if '"lat"' not in t:
            continue
        j = json.loads(t.split(");")[0].replace("&quot;", "'"))
        location_name = j.get("title")
        raw_address = j.get("address") or ""
        street_address, city, state, postal = get_international(raw_address)
        store_number = j.get("store_number")
        phone = j.get("phone")
        latitude = j.get("lat")
        longitude = j.get("lng")

        hours = j.get("note") or ""
        hours = hours.replace("Opens Daily from", "Monday-Sunday,").replace("to", "-")
        if "(" in hours:
            hours = hours.split("(")[0].strip()
        hours_of_operation = hours or "Monday-Sunday, 10.00am - 10.00pm"

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code="MY",
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
    locator_domain = "https://www.decathlon.my/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
