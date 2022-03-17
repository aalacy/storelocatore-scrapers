from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='span4']")

    for d in divs:
        location_name = "".join(d.xpath(".//h2/text()")).strip()
        line = d.xpath(".//p/text()")
        line = list(filter(None, [l.strip() for l in line]))
        csz = line.pop()
        city = csz.split(",")[0].strip()
        csz = csz.split(",")[1].strip()
        state, postal = csz.split()
        street_address = ", ".join(line)
        phone = "".join(d.xpath(".//dd[contains(@class, 'phone')]//text()")).strip()

        hours = d.xpath(".//dd[contains(@class, 'hours')]//text()")
        hours = list(filter(None, [h.strip() for h in hours]))
        hours_of_operation = ";".join(hours)
        if ";Drive" in hours_of_operation:
            hours_of_operation = hours_of_operation.split(";Drive")[0].strip()

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
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.meatheadsburgers.com/"
    page_url = "https://www.meatheadsburgers.com/locations"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        fetch_data(writer)
