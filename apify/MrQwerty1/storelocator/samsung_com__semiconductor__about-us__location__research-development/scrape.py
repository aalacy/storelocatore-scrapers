from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()
    city = adr.city
    state = adr.state or SgRecord.MISSING
    postal = adr.postcode

    return street_address, city, state, postal


def fetch_data(sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath(
        "//h2[./span[contains(text(), 'R&D')]]/following-sibling::div//div[@class='centers-item']"
    )

    for d in divs:
        location_name = "".join(d.xpath(".//strong/text()")).strip()

        _tmp = []
        lines = d.xpath(".//p[@class='item-desc']/text()")
        for line in lines:
            if not line.strip():
                continue
            line = " ".join(line.split())
            _tmp.append(line)

        raw_address = "".join(_tmp)
        street_address, city, state, postal = get_international(raw_address)
        if state[0].isdigit():
            postal = state
            state = SgRecord.MISSING

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            locator_domain=locator_domain,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = (
        "https://www.samsung.com/semiconductor/about-us/location/manufacturing-centers/"
    )
    page_url = locator_domain
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
