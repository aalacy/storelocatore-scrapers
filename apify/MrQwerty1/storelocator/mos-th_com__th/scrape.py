from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
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


def get_coords_from_embed(text):
    try:
        latitude = text.split("!3d")[1].strip().split("!")[0].strip()
        longitude = text.split("!2d")[1].strip().split("!")[0].strip()
    except IndexError:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    return latitude, longitude


def fetch_data(sgw: SgWriter):
    page_url = "https://www.mos-th.com/en/branch/"
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    divs = tree.xpath("//div[contains(@class, 'branch-detail branch')]")
    for d in divs:
        location_name = "".join(d.xpath(".//h2/text()")).strip()
        raw_address = "".join(
            d.xpath(".//h2/following-sibling::div[1]//text()")
        ).strip()
        if "\r" in raw_address:
            raw_address = raw_address.split("\r")[0].strip()
        street_address, city, state, postal = get_international(raw_address)
        phone = "".join(d.xpath(".//h2/following-sibling::div[2]//text()")).strip()

        text = "".join(d.xpath(".//iframe/@data-src"))
        latitude, longitude = get_coords_from_embed(text)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="TH",
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.mos-th.com/"
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
