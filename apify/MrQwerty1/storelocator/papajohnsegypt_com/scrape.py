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
    state = adr.state
    postal = adr.postcode

    return street_address, city, state, postal


def fetch_data(sgw: SgWriter):
    page_url = "http://www.papajohnsegypt.com/branches.php"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='column']")

    for d in divs:
        name = "".join(d.xpath("./h2/text()")).strip()
        blocks = d.xpath(".//div[@class='pizza-description']/p")
        for b in blocks:
            raw_address = "".join(b.xpath("./text()")).strip() + f", {name}"
            street_address, city, state, postal = get_international(raw_address)
            if len(street_address) < 5:
                street_address = ",".join(raw_address.split(",")[:-1])

            row = SgRecord(
                page_url=page_url,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code="EG",
                locator_domain=locator_domain,
                raw_address=raw_address,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "http://www.papajohnsegypt.com/"
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
