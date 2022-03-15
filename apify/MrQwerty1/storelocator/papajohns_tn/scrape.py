from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    page_url = "http://www.papajohns.tn/calltoorder"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'var locations =')]/text()"))
    divs = eval(text.split("var locations =")[1].split("];")[0] + "]")

    for d in divs:
        line = d[0]
        location_name = line.split(" | ")[0].strip()
        phone = line.split(":")[1].split("<br>")[0].strip()
        latitude = d[1]
        longitude = d[2]
        hours_of_operation = ";".join(line.split("<br>")[1:]).replace(" ;", ";").strip()

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            country_code="TN",
            phone=phone,
            latitude=str(latitude),
            longitude=str(longitude),
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "http://www.papajohns.tn/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
