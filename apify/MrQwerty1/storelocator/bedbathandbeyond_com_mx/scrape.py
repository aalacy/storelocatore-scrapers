from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    if ":" in line:
        postal = line.split(":")[1].split(",")[0].strip()
        adr = parse_address(International_Parser(), line, postcode=postal)
    else:
        adr = parse_address(International_Parser(), line)
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()
    city = adr.city or ""
    state = adr.state
    postal = adr.postcode

    return street_address, city, state, postal


def fetch_data(sgw: SgWriter):
    page_url = "https://www.bedbathandbeyond.com.mx/stores"
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    divs = tree.xpath("//ol[@class='store-list']/li")
    for d in divs:
        location_name = "".join(d.xpath(".//h5/text()")).strip()
        raw_address = "".join(d.xpath(".//div[@class='address']/p[1]/text()")).strip()
        street_address, city, state, postal = get_international(raw_address)
        phone = (
            "".join(d.xpath(".//div[@class='address']/p[last()]/text()"))
            .replace("Tel.:", "")
            .strip()
        )
        text = "".join(d.xpath(".//iframe/@src"))
        latitude, longitude = text.split("q=")[1].split("&")[0].split(",")
        hours_of_operation = "".join(
            d.xpath(".//div[@class='schedule']/p/text()")
        ).strip()

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="MX",
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.bedbathandbeyond.com.mx/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
