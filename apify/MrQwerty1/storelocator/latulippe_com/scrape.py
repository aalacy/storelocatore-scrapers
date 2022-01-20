from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    page_url = "https://latulippe.com/en/our-stores/"
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    divs = tree.xpath("//div[@class='magasin-item']")
    for d in divs:
        location_name = "".join(d.xpath(".//h2/text()")).strip()
        line = d.xpath(".//h2/following-sibling::p[1]/text()")
        line = list(filter(None, [l.strip() for l in line]))
        postal = line.pop().split(", ")[-1]
        city, state = line.pop().split(", ")
        street_address = ", ".join(line)
        phone = "".join(
            d.xpath(".//b[contains(text(), 'Phone')]/following-sibling::text()[1]")
        ).strip()

        _tmp = []
        days = d.xpath(".//th/text()")
        inters = d.xpath(".//td/text()")
        for day, inter in zip(days, inters):
            _tmp.append(f"{day}: {inter}")
        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="CA",
            phone=phone,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://latulippe.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        fetch_data(writer)
