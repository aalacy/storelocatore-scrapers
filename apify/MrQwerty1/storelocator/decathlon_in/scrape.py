from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    page_url = "https://www.decathlon.in/cms/decathlon-stores-2020"
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    states = tree.xpath("//div[@class='container table-p']")
    for st in states:
        state = "".join(st.xpath(".//p/text()")).strip()

        divs = st.xpath(
            ".//tr[./td[contains(@class, 'green')] or ./td/span[contains(@class, 'green')]]"
        )
        for d in divs:
            location_name = "".join(d.xpath(".//th/text()")).strip()
            city = "".join(d.xpath(".//td[1]/text()")).strip()
            hours_of_operation = ";".join(d.xpath(".//td[3]/text()")).strip()
            phone = "".join(d.xpath(".//td[last()]/text()")).strip()

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                city=city,
                state=state,
                country_code="IN",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.decathlon.in/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        fetch_data(writer)
