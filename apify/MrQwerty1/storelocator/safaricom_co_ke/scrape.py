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


def fetch_data(sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    types = tree.xpath("//li[./a[@href='#one']]/following-sibling::li/a")
    for t in types:
        location_type = "".join(t.xpath("./text()"))
        href = "".join(t.xpath("./@href")).replace("#", "")
        divs = tree.xpath(
            f"//div[@id={href}]//div[@class='col-12 col-md-4 col-sm-6 promo-search']"
        )

        for d in divs:
            location_name = "".join(d.xpath(".//h2/text()")).strip()
            raw_address = "".join(d.xpath(".//p/text()")).strip()
            street_address, city, state, postal = get_international(raw_address)

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                location_type=location_type,
                country_code="KE",
                locator_domain=locator_domain,
                raw_address=raw_address,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.safaricom.co.ke/"
    page_url = "https://www.safaricom.co.ke/personal/index.php/safaricom-shop"
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
