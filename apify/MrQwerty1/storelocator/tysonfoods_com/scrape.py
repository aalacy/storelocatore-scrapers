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
    postal = adr.postcode or SgRecord.MISSING
    country = adr.country or SgRecord.MISSING

    return street_address, city, state, postal, country


def fetch_data(sgw: SgWriter):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    countries = tree.xpath("//div[contains(@class, 'brick brick-accordion_panel')]")

    for c in countries:
        divs = c.xpath(".//div[@class='brick brick-dynamic_column']")
        country = "".join(
            c.xpath(
                ".//div[@class='field field--name-title field--type-string field--label-hidden field__item']/text()"
            )
        ).strip()

        for d in divs:
            location_name = "".join(d.xpath(".//p/strong/text()")).strip()
            if not location_name:
                location_name = country

            phone = SgRecord.MISSING
            lines = d.xpath(".//p/text()")
            lines = list(filter(None, [line.strip() for line in lines]))
            line = lines[-1]

            if line.startswith("+") or line[0].isdigit() or "Phone" in line:
                phone = "".join(
                    lines.pop().replace("Phone:", "").replace("TYSON", "").split()
                )

            raw_address = ", ".join(lines).replace(",,", ",")
            street_address, city, state, postal, country_code = get_international(
                raw_address
            )
            if country_code == SgRecord.MISSING:
                country_code = country
            if postal == SgRecord.MISSING and country_code == "Mexico":
                postal = raw_address.split(",")[-2].strip()

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
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.tysonfoods.com/"
    page_url = "https://www.tysonfoods.com/contact-us"
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
