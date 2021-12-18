from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import parse_address_intl

locator_domain = "https://www.tysonfoods.com/"
page_url = "https://www.tysonfoods.com/contact-us"


def fetch_data(sgw, session):
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
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2

            if country_code == SgRecord.MISSING:
                country_code = country
            if postal == SgRecord.MISSING and country_code == "Mexico":
                postal = raw_address.split(",")[-2].strip()

            sgw.write_row(
                SgRecord(
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=addr.city,
                    state=addr.state,
                    zip_postal=addr.postcode,
                    country_code=addr.ubuntu,
                    phone=phone,
                    locator_domain=locator_domain,
                    raw_address=raw_address,
                )
            )


if __name__ == "__main__":
    with SgRequests() as session:

        with SgWriter(
            SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
        ) as writer:
            fetch_data(writer, session)
