from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
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
    page_url = "https://pretamanger.be/fr-be/nous-trouver"
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[contains(@class, 'tabs-section')]")
    for d in divs:
        location_name = "".join(
            d.xpath(".//div[@class='row']/h3[not(@class)]/text()")
        ).strip()
        raw_address = "".join(
            d.xpath(
                ".//div[@class='row']/h3[not(@class)]/following-sibling::p[1]/text()"
            )
        ).strip()
        street_address, city, state, postal = get_international(raw_address)
        phone = "".join(d.xpath(".//a[@class='telephone']/text()")).strip()
        latitude, longitude = d.xpath(".//div[@data-position]/@data-position")[0].split(
            ","
        )
        hours_of_operation = d.xpath(
            ".//h3[@class='opening-title']/following-sibling::p/text()"
        )[0].strip()

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="BE",
            phone=phone,
            latitude=latitude.strip(),
            longitude=longitude.strip(),
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    locator_domain = "https://pretamanger.be/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
