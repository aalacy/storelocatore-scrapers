from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    page_url = "https://www.paul.fr/default/nos-restaurants"
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//table//tr")
    divs.pop(0)

    for d in divs:
        location_name = "".join(d.xpath("./td[1]/text()")).strip()
        street_address = "".join(d.xpath("./td[2]/text()")).strip()
        postal = "".join(d.xpath("./td[3]/text()")).strip()
        city = "".join(d.xpath("./td[4]/text()")).strip()
        phone = "".join(d.xpath("./td[5]/text()")).strip()

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code="FR",
            phone=phone,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.paul.fr/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        fetch_data(writer)
