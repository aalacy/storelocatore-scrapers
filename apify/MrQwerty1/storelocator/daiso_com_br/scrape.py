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
    page_url = "https://www.daiso.com.br/institucional/2112/8481"
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    divs = tree.xpath("//ul[.//strong]")
    for d in divs:
        location_name = "".join(d.xpath(".//text()")).split(".")[-1].strip()
        store_number = "".join(d.xpath(".//text()")).split(".")[0].strip()
        raw_address = (
            "".join(d.xpath("./following-sibling::p[1]//text()"))
            .replace("/", ",")
            .strip()
        )
        street_address, city, state, postal = get_international(raw_address)
        hours = d.xpath(
            "./following-sibling::p[position()>1 and position()<=3]//text()"
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
            country_code="BR",
            store_number=store_number,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.daiso.com.br/"
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
