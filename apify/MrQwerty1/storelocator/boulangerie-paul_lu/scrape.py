from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    page_url = "https://boulangerie-paul.lu/en/shop/our-shops"
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[contains(@class, 'checkboard ')]")

    for d in divs:
        location_name = "".join(d.xpath(".//h2/text()")).strip()
        line = d.xpath(".//h2/following-sibling::p[1]/text()")
        line = list(filter(None, [l.strip() for l in line]))
        street_address = line.pop(0)
        if street_address.endswith(","):
            street_address = street_address[:-1]

        postal, city = line.pop().split()
        phone = "".join(d.xpath(".//a[contains(@href, 'tel:')]/text()")).strip()
        hours = d.xpath(".//li/text()")
        hours = list(filter(None, [h.strip() for h in hours]))
        hours_of_operation = ";".join(hours)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code="LU",
            phone=phone,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://boulangerie-paul.lu/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        fetch_data(writer)
