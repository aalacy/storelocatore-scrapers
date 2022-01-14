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
    urls = [
        "https://www.handelsbanken.com/en/about-the-group/locations/poland",
        "https://www.handelsbanken.com/en/about-the-group/locations/spain",
        "https://www.handelsbanken.com/en/about-the-group/locations/united-states",
    ]

    for page_url in urls:
        r = session.get(page_url)
        tree = html.fromstring(r.text)

        line = tree.xpath("//h3[text()='Address']/following-sibling::div//text()")
        line = list(filter(None, [l.strip() for l in line]))
        country = line.pop()
        location_name = f"Handelsbanken {country}"
        raw_address = ", ".join(line)
        street_address, city, state, postal = get_international(raw_address)
        phone = (
            tree.xpath("//p[contains(text(), 'Tel:')]/text()")[0]
            .replace("Tel:", "")
            .strip()
        )

        _tmp = []
        hours = tree.xpath(
            "//h3[text()='Opening hours']/following-sibling::div//text()"
        )
        for h in hours:
            if not h.strip() or "appointment" in h:
                continue
            _tmp.append(h.strip())

        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country,
            phone=phone,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://racewaycarwash.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
