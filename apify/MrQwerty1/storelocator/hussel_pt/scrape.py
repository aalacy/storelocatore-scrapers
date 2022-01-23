import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    post = line.split(", ")[-1].split()[0]
    adr = parse_address(International_Parser(), line, postcode=post)
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()
    city = adr.city
    state = adr.state
    postal = adr.postcode

    return street_address, city, state, postal


def fetch_data(sgw: SgWriter):
    r = session.get("https://www.hussel.pt/lojas", headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'var stores_obj')]/text()"))
    text = text.split("JSON.parse('")[1].split("');")[0]
    js = json.loads(text)

    for j in js:
        location_name = j.get("title")
        latitude = j.get("lat")
        longitude = j.get("lng")
        phone = j.get("phone")
        page_url = j.get("link")
        source = j.get("address") or "<html></html>"
        source = source.replace("</br>", "<br/>")
        root = html.fromstring(source)
        lines = root.xpath("//text()")
        if ", " not in lines[1]:
            store_number = lines.pop(1).split("Loja ")[1].split()[0]
        else:
            _tmp = lines.pop(1)
            store_number = _tmp.split("Loja ")[1].split()[0]
            lines.insert(1, _tmp.split(", ")[0])

        raw_address = ", ".join(lines)
        street_address, city, state, postal = get_international(raw_address)
        street_address = lines.pop(1)
        hours = j.get("schedule") or ""
        hours_of_operation = hours.replace("</br>", ";")

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="PT",
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
    locator_domain = "https://www.hussel.pt/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
    }

    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
