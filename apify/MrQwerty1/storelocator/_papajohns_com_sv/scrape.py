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


def get_coords_from_embed(text):
    try:
        latitude = text.split("!3d")[1].strip().split("!")[0].strip()
        longitude = text.split("!2d")[1].strip().split("!")[0].strip()
    except IndexError:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    return latitude, longitude


def fetch_data(sgw: SgWriter):
    page_url = "https://www.papajohns.com.sv/site/restaurantes.html"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='stores' and .//a]")

    for d in divs:
        location_name = "".join(d.xpath(".//a[@data-info-name]/@data-info-name"))
        raw_address = "".join(d.xpath(".//a[@data-info-dir]/@data-info-dir"))
        street_address, city, state, postal = get_international(raw_address)
        store_number = "".join(d.xpath(".//a[@data-info-id]/@data-info-id"))
        text = "".join(d.xpath(".//a[@data-info-url]/@data-info-url"))
        latitude, longitude = get_coords_from_embed(text)
        hours_of_operation = (
            "".join(d.xpath(".//a[@data-info-hours]/@data-info-hours"))
            .replace("|", " ")
            .replace("::", ";")
        )
        if hours_of_operation.endswith(";"):
            hours_of_operation = hours_of_operation[:-1]

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="SV",
            store_number=store_number,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.papajohns.com.sv/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
