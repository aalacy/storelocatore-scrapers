from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID


def fetch_data(sgw: SgWriter):
    page_url = "http://www.pinkberrylondon.co.uk/"
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='table2']")

    for d in divs:
        line = "".join(d.xpath(".//h2//text()")).split(",")
        line.pop()
        location_name = line.pop(0).strip()
        city = "London"
        street_address = line.pop(0).replace(city, "").strip()
        try:
            postal = line.pop().strip()
        except IndexError:
            postal = SgRecord.MISSING

        _tmp = []
        tr = d.xpath(".//tr")
        for t in tr:
            day = "".join(t.xpath("./th/text()")).strip()
            inter = "".join(t.xpath("./td/text()")).strip()
            _tmp.append(f"{day} {inter}")
        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code="GB",
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "http://www.pinkberrylondon.co.uk/"
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
