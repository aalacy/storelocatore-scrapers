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
    page_url = "https://www.daiso.com.tw/Inside/Store"
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    divs = tree.xpath("//li[@data-storeid]")
    for d in divs:
        location_name = "".join(d.xpath(".//h1/a/text()")).strip()
        raw_address = "".join(d.xpath(".//p[@data-store='address']/text()")).strip()
        street_address, city, state, postal = get_international(raw_address)

        phone = "".join(d.xpath(".//h3[@data-store='telphone']/text()")).strip()
        latitude = "".join(d.xpath(".//input[@data-store='lat']/@value"))
        longitude = "".join(d.xpath(".//input[@data-store='lng']/@value"))
        hours_of_operation = "".join(
            d.xpath(".//h2[@data-store='opentime']/text()")
        ).strip()

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="TW",
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.daiso.com.tw/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        fetch_data(writer)
