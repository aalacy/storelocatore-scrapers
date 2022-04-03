from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    r = session.get(locator_domain)
    tree = html.fromstring(r.text)

    divs = tree.xpath("//div[@data-ux='ContentCard' and ./div/h4]")
    for d in divs:
        location_name = d.xpath(".//h4/text()")[0].strip()
        line = d.xpath("./div[2]//text()")
        line = list(filter(None, [l.strip() for l in line]))
        if line[0][0].isdigit():
            street_address = line.pop(0)
        else:
            street_address = location_name

        csz = line.pop(0)
        city = csz.split(", ")[0].strip()
        csz = csz.split(", ")[1].strip()
        state, postal = csz.split()

        phone = line.pop(0)
        hours_of_operation = ";".join(line)

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
    locator_domain = page_url = "https://juliobertos.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        fetch_data(writer)
