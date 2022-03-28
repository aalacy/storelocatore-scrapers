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
    postal = adr.postcode

    return street_address, city, postal


def fetch_data(sgw: SgWriter):
    page_url = "https://www.amway.in/contactUs"
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    divs = tree.xpath("//template[@slot='header']")
    for di in divs:
        state = "".join(di.xpath("./text()")).strip()
        for d in di.xpath("./following-sibling::template[1]/div[./div]"):
            location_name = "".join(
                d.xpath(".//div[@class='contact-us-component-city-title']/text()")
            ).strip()
            raw_address = " ".join(
                d.xpath(
                    ".//div[@class='contact-us-component-address-title']/following-sibling::div//text()"
                )
            ).strip()
            street_address, city, postal = get_international(raw_address)

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code="IN",
                locator_domain=locator_domain,
                raw_address=raw_address,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.amway.in/"
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
