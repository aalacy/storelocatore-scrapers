from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    adr1 = adr.street_address_1 or ""
    adr2 = adr.street_address_2 or ""
    street = f"{adr1} {adr2}".strip()
    postal = adr.postcode or SgRecord.MISSING

    return street, postal


def parse_block(g, country, sgw):
    location_name = "".join(g.xpath(".//h2/text()")).strip()
    raw_address = "".join(g.xpath(".//h3/text()")).strip()
    city = SgRecord.MISSING
    if "-" in raw_address:
        city = raw_address.split("-")[0]
    street_address, postal = get_international(raw_address)
    hours_of_operation = "".join(g.xpath(".//p/text()")).strip()

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        zip_postal=postal,
        country_code=country,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
        raw_address=raw_address,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    gl = tree.xpath(
        "//div[./div/div/h2[contains(text(), 'Visit')]]/following-sibling::div"
    )
    country = SgRecord.MISSING

    for g in gl:
        check = g.xpath(".//h2/text()")
        if not check:
            continue
        if len(check) == 1:
            if "Locations" in check[0]:
                country = check[0].replace("Locations in", "").strip()
                continue
            else:
                parse_block(g, country, sgw)
        else:
            divs = g.xpath(".//div[@class='st-two-column__column']")
            for d in divs:
                parse_block(d, country, sgw)


if __name__ == "__main__":
    locator_domain = "https://www.samsung.com/levant/"
    page_url = "https://www.samsung.com/levant/samsung-experience-store/locations/"
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
