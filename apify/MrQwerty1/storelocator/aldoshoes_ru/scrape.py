from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    page_url = "https://aldoshoes.ru/stores/"
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    divs = tree.xpath("//div[@class='stories-itm']")
    for d in divs:
        location_name = "".join(d.xpath("./b/text()")).strip()
        line = d.xpath("./text()")
        line = list(filter(None, [l.strip() for l in line]))
        hours_of_operation = (
            line.pop().replace("Открыт с", "").replace(" до ", "-").strip()
        )
        phone = line.pop()
        street_address = " ".join(line[1:])
        city = location_name

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            country_code="RU",
            phone=phone,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://aldoshoes.ru/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        fetch_data(writer)
