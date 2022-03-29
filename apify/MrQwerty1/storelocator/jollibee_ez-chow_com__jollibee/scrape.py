from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    page_url = "https://jollibee.ez-chow.com/jollibee/locations"
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    divs = tree.xpath("//div[@class='row' and ./h2]")
    for d in divs:
        location_name = "".join(d.xpath("./h2/text()")).strip()
        raw_address = d.xpath(".//h3[@class='address']/text()")[0].strip()
        phone = d.xpath(".//h3[@class='address']/text()")[1].strip()
        street_address = raw_address.split(", ")[0].replace("Guam", "")
        city = "Guam"
        state, postal = raw_address.split(", ")[-1].split()
        hours_of_operation = d.xpath(".//h3[@class='address']//text()")[2].strip()

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="GU",
            phone=phone,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://jollibee.ez-chow.com/jollibee/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
