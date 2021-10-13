from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    api_url = "https://www.rag-bone.com/stores"

    r = session.get(api_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='sl-store clearfix sl__store']")

    for d in divs:
        slug = "".join(d.xpath(".//a[@class='sl__store-details-name']/@href"))
        page_url = f"https://www.rag-bone.com{slug}"
        street_address = "".join(
            d.xpath(".//div[@itemprop='streetAddress']/text()")
        ).strip()
        city = "".join(d.xpath(".//span[@itemprop='addressLocality']/text()")).strip()
        state = "".join(d.xpath(".//span[@itemprop='addressRegion']/text()")).strip()
        postal = "".join(d.xpath(".//span[@itemprop='postalCode']/text()")).strip()
        phone = "".join(d.xpath(".//span[@itemprop='telephone']/text()")).strip()

        if len(postal) == 5:
            country_code = "US"
        elif phone.startswith("+44"):
            country_code = "GB"
        else:
            country_code = SgRecord.MISSING

        location_name = "".join(
            d.xpath(".//a[@class='sl__store-details-name']/text()")
        ).strip()

        text = "".join(d.xpath(".//*[@data-pin]/@data-pin"))
        try:
            lat_lon = eval(text)
            latitude, longitude = lat_lon[1:3]
        except:
            latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

        hours = d.xpath(
            ".//div[@class='sl__store-details-hours sl__store-details-txt']/text()|.//div[text()='Store Hours']/following-sibling::p[1]/text()"
        )
        hours = list(filter(None, [h.strip() for h in hours]))
        hours_of_operation = ";".join(hours) or "Closed"

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.rag-bone.com/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
