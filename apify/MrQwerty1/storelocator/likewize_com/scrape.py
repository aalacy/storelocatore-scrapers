from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    street = f"{adr.street_address_1} {adr.street_address_2}".replace(
        "None", ""
    ).strip()
    city = adr.city or SgRecord.MISSING
    state = adr.state
    postal = adr.postcode or ""
    country = adr.country or ""

    return street, city, state, postal, country


def fetch_data(sgw: SgWriter):
    page_url = "https://likewize.com/contact-us/"
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//h3[@class='elementor-icon-box-title']")

    for d in divs:
        location_name = "".join(d.xpath(".//text()")).strip()
        lines = d.xpath("./following-sibling::p/text()")
        lines = list(filter(None, [line.strip() for line in lines]))
        phone = SgRecord.MISSING
        if lines[-1].startswith("(") or lines[-1].startswith("+"):
            phone = lines.pop()

        raw_address = ", ".join(lines)
        street_address, city, state, postal, country = get_international(raw_address)
        postal = postal.replace("C.P.", "").strip()
        if not country and ("–" in location_name or "," in location_name):
            if len(postal) == 5:
                country = "US"
            else:
                country = "CA"
        else:
            country = location_name
            if "–" in country:
                country = country.split("–")[0].strip()

        if country == "India" and city == SgRecord.MISSING:
            city = raw_address.split(", ")[-2]
        if country == "Peru" and city == SgRecord.MISSING:
            city = raw_address.split(", ")[-1]

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            phone=phone,
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
    locator_domain = "https://likewize.com/"
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
