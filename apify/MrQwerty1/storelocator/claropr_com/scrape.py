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
    city = adr.city or SgRecord.MISSING
    state = adr.state or SgRecord.MISSING
    postal = adr.postcode or SgRecord.MISSING

    return street, city, state, postal


def fetch_data(sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//h3[contains(text(), 'Dirección')]/following-sibling::ul/li")
    hoos = tree.xpath("//h3[contains(text(), 'Horarios')]/following-sibling::ul/li")

    for d, h in zip(divs, hoos):
        location_name = "".join(d.xpath(".//h3/text()")).strip()
        raw_address = "".join(d.xpath(".//p/text()")).strip()
        phone = "".join(d.xpath(".//a/text()")).replace("TEL.", "").strip()
        street_address, city, state, postal = get_international(raw_address)
        country_code = "PR"
        hours_of_operation = " ".join("".join(h.xpath(".//text()")).split())

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            phone=phone,
            locator_domain=locator_domain,
            raw_address=raw_address,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.claropr.com/"
    page_url = "https://www.claropr.com/personas/soporte/atencion-cliente/tiendas/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
