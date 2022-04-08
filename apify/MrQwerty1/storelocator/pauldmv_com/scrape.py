import ssl
import time
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgselenium import SgChrome
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
    page_url = "https://www.pauldmv.com/locations"
    with SgChrome() as fox:
        fox.get(page_url)
        locations = fox.find_elements_by_class_name("dmGeoMLocItem")
        for loc in locations:
            loc.click()
            time.sleep(1)
            source = fox.page_source
            tree = html.fromstring(source)
            location_name = "".join(
                tree.xpath(".//div[@class='dmGeoSVTitle']//text()")
            ).strip()
            phone = "".join(tree.xpath(".//a[@phone]/@phone"))
            raw_address = "".join(
                tree.xpath("//div[@class='dmGeoSVAddr']/text()")
            ).replace(f", {phone}", "")
            street_address, city, state, postal = get_international(raw_address)

            hours = tree.xpath(".//div[@class='dmGeoSVMoreInfo']/text()")
            hours = list(filter(None, [h.strip() for h in hours]))
            hours_of_operation = ";".join(hours).replace(" // ", ";")
            fox.find_element_by_class_name("dmGeoSVSeeAll").click()
            time.sleep(1)

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.pauldmv.com/"
    ssl._create_default_https_context = ssl._create_unverified_context
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        fetch_data(writer)
