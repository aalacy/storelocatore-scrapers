from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
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
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    divs = tree.xpath(
        "//div[count(./section)>5]/section[.//*[contains(text(), 'Trading Hours')]]"
    )
    for d in divs:
        lines = d.xpath(".//text()")
        lines = list(
            filter(
                None,
                [li.replace("\xa0", " ").replace("\u200b", "").strip() for li in lines],
            )
        )
        location_name = " ".join(lines[: lines.index("Trading Hours:")])
        hours_of_operation = ";".join(
            lines[lines.index("Trading Hours:") + 1 : lines.index("Address:")]
        )
        raw_address = " ".join(
            lines[lines.index("Address:") + 1 : lines.index("Phone:")]
        )
        phone = lines[lines.index("Phone:") + 1]
        street_address, city, state, postal = get_international(raw_address)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="NZ",
            phone=phone,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.daiso.nz/"
    page_url = locator_domain
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        fetch_data(writer)
