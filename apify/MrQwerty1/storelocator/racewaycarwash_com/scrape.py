from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://racewaycarwash.com/locations/"
    r = session.get(api)
    tree = html.fromstring(r.text)

    divs = tree.xpath("//li[@class='location']")
    for d in divs:
        location_name = "".join(d.xpath(".//div[@class='logo']/h4/text()")).strip()
        page_url = "".join(d.xpath(".//div[@class='more']/a/@href"))
        street_address = "".join(d.xpath(".//span[@class='line-1']/text()")).strip()
        phone = "".join(d.xpath(".//span[@class='line-phone']/a/text()")).strip()
        csz = "".join(d.xpath(".//span[@class='line-csz']/text()")).strip()
        city = csz.split(",")[0].strip()
        csz = csz.split(",")[1].strip()
        state = csz.split()[0]
        postal = csz.split()[1]
        latitude = "".join(d.xpath(".//span[@data-lat]/@data-lat"))
        longitude = "".join(d.xpath(".//span[@data-lat]/@data-lng"))
        hours = d.xpath(".//div[@class='info']/text()")
        hours = list(filter(None, [h.strip() for h in hours]))
        hours_of_operation = ";".join(hours)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="US",
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://racewaycarwash.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
