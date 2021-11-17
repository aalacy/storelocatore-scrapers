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

    divs = tree.xpath(
        "//table[@class='table table-striped table-bordered mb-0 text-center']//tr[./td]"
    )
    for d in divs:
        location_name = "".join(d.xpath("./td[2]//text()")).strip()
        street_address = "".join(d.xpath("./td[3]//text()")).strip()
        state = "".join(d.xpath("./td[1]//text()")).strip()

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
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
