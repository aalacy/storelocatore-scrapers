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
    api = "https://www.papajohns.com.do/restaurantes.html"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//tr[./td[@height='111']]/td")

    for d in divs:
        slug = "".join(d.xpath(".//a[./img]/@href"))
        if slug:
            page_url = f"https://www.papajohns.com.do/{slug}"
        else:
            page_url = api
        location_name = "".join(
            d.xpath(".//strong[@class='nosotroseleccionado']/text()")
        ).strip()
        raw_address = "".join(d.xpath(".//td[@height='44']/text()")).strip()
        street_address, city, state, postal = get_international(raw_address)
        phone = "".join(
            d.xpath(".//td[@class='nosotroseleccionado']/strong/text()")
        ).strip()
        hours = d.xpath(
            ".//td[@align='right' and not(@width) and not(./strong)]/preceding-sibling::td//text()"
        )
        hours = list(filter(None, [h.strip() for h in hours]))
        hours_of_operation = ";".join(hours)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            phone=phone,
            country_code="DO",
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.papajohns.com.do/"
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
