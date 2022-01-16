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
    page_url = "https://www.mos.jp/shop/foreign/"
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    divs = tree.xpath(
        "//h3[@class='headingThirdly']/following-sibling::table[1]/tbody/tr|//h2[@id='PH']/following-sibling::table[1]/tbody/tr"
    )
    for d in divs:
        location_name = "".join(d.xpath("./th/text()")).strip()
        raw_address = " ".join(" ".join(d.xpath("./td/text()")).split())
        street_address, city, state, postal = get_international(raw_address)
        country = "CN"
        if "," in raw_address:
            country = "PH"

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country,
            locator_domain=locator_domain,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.mos.jp/shop/foreign/"
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
