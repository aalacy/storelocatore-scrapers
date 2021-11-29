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
    hoos = dict()
    api = "https://storemapper-herokuapp-com.global.ssl.fastly.net/api/users/11232/stores.js"

    req = session.get(page_url)
    root = html.fromstring(req.text)
    stores = root.xpath("//div[@class='store']")
    for s in stores:
        p = html.fromstring("".join(s.xpath("./@data-address"))).xpath(".//text()")[-1]
        p = p.replace("(", "").replace(")", "").replace(" ", "").lower()
        if "ext" in p:
            p = p.split("ext")[0]
        key = p[-8:]
        text = "".join(s.xpath("./@data-opening")) or "<html></html>"
        try:
            hours = html.fromstring(text).xpath(".//text()")[-2].replace(":00 ", ":00;")
            hoos[key] = hours
        except IndexError:
            pass

    r = session.get(api)
    js = r.json()["stores"]

    for j in js:
        location_name = j.get("name")
        raw_address = j.get("address")
        phone = j.get("phone") or ""
        key = phone.replace(" ", "")[-8:]
        hours_of_operation = hoos.get(key)
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        store_number = j.get("custom_field_1")
        street_address, city, state, postal = get_international(raw_address)
        if not city:
            city = raw_address.split(", ")[1]

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="GB",
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            store_number=store_number,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.frenchconnection.com/"
    page_url = "https://www.frenchconnection.com/pages/store-locator"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        fetch_data(writer)
