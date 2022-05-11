from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.moreyoga.co.uk/studios/"
    r = session.get(api)
    tree = html.fromstring(r.text)

    phone = "".join(tree.xpath("//span[@id='et-info-phone']/text()")).strip()
    divs = tree.xpath("//div[./a[contains(text(), 'STUDIO')]]")
    for d in divs:
        line = d.xpath("./preceding-sibling::div[1]//text()")
        line = list(filter(None, [l.strip() for l in line]))
        location_name = line.pop(0)
        postal = line.pop().replace("London", "").strip()
        street_address = " ".join(line)
        city = "London"
        page_url = "".join(d.xpath(".//a/@href"))

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code="GB",
            phone=phone,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.moreyoga.co.uk/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
