import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address, International_Parser


def get_city(line):
    adr = parse_address(International_Parser(), line)
    city = adr.city or ""

    return city


def rem(text):
    if text.endswith(","):
        return text[:-1]
    return text


def fetch_data(sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'stores:')]/text()"))
    text = text.split("stores:")[1].split("}],")[0] + "}]"
    js = json.loads(text)

    for j in js:
        adr1 = j.get("address_line_1") or ""
        adr2 = j.get("address_line_2") or ""
        street_address = f"{adr1} {adr2}".strip()
        if not adr1:
            street_address = j.get("address_name") or ""

        street_address = rem(street_address)
        city = j.get("address_city") or ""
        if not city:
            ad = j.get("address") or ""
            ad = ad.replace("\r\n", "").replace("<br />", " ")
            city = get_city(ad).replace("Co.", "").strip()

        city = rem(city)
        postal = j.get("address_post_code")
        country_code = "IE"
        store_number = j.get("id")
        location_name = j.get("title")
        phone = j.get("telephone")
        latitude = j.get("latitude")
        longitude = j.get("longitude")

        hours = j.get("opening_hours") or ""
        hours_of_operation = hours.replace("<br />\r\n", ";")
        if hours_of_operation.endswith(";"):
            hours_of_operation = rem(hours_of_operation)

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
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://supervalu.ie/"
    page_url = "https://supervalu.ie/store-locator"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
