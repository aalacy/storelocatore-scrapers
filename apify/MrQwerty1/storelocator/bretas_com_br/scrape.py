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
    page_url = "https://www.bretas.com.br/lojas/"
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@store]")

    for d in divs:
        raw_address = "".join(d.xpath(".//p[@class='content']/text()")).strip()
        street_address, city, state, postal = get_international(raw_address)
        country_code = "BR"
        location_name = "".join(d.xpath(".//h4/text()")).strip()
        phone = "".join(d.xpath(".//a[@class='telefone']/text()")).strip()
        if "/" in phone:
            phone = phone.split("/")[0].strip()

        store_number = "".join(d.xpath("./@store"))
        latitude = "".join(d.xpath("./@lat"))
        longitude = "".join(d.xpath("./@lng"))

        hours = d.xpath(".//p[@class='content']/span/text()")
        hours = list(filter(None, [h.strip() for h in hours]))
        hours_of_operation = ";".join(hours)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.bretas.com.br/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests(proxy_country="br")
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
