from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID


def fetch_data(sgw: SgWriter):
    page_url = "https://web.vodafone.com.eg/en/stores-new"
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    divs = tree.xpath("//div[@id='accordionExample']/div")
    for d in divs:
        city = "".join(d.xpath(".//h4/span/text()")).strip()
        tr = d.xpath(".//tr[./td]")
        for t in tr:
            location_name = "".join(t.xpath("./td[2]//text()")).strip()
            street_address = "".join(t.xpath("./td[3]//text()")).strip()
            state = "".join(t.xpath("./td[1]//text()")).strip()

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                country_code="EG",
                locator_domain=locator_domain,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://web.vodafone.com.eg/"
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        fetch_data(writer)
