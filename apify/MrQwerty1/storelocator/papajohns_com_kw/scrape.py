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
    city = adr.city
    state = adr.state
    postal = adr.postcode

    return street_address, city, state, postal


def fetch_data(sgw: SgWriter):
    page_url = "http://papajohns.com.kw/locations/"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(
        tree.xpath("//script[contains(text(), 'maplistScriptParamsKo')]/text()")
    )
    text = text.split("maplistScriptParamsKo =")[1].split("};")[0] + "}"
    js = json.loads(text)["KOObject"][0]["locations"]

    for j in js:
        location_name = j.get("title")
        store_number = j.get("cssClass").split("-")[-1]
        source = j.get("address") or "<html></html>"
        root = html.fromstring(source)
        raw_address = "".join(root.xpath("//text()")).replace("\n", "").strip()
        street_address, city, state, postal = get_international(raw_address)
        phone = j.get("maplistTelephone")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        hours_of_operation = j.get("maplistHours")

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
            zip_postal=postal,
            country_code="KW",
            store_number=store_number,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "http://papajohns.com.kw/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
