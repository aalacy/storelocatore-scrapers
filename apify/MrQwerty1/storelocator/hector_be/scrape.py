from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://hector.be/restaurant/"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[contains(@itemtype, 'Restaurant')]")

    for d in divs:
        location_name = "".join(d.xpath(".//h3[@itemprop='name']/a/text()")).strip()
        page_url = "".join(d.xpath(".//h3[@itemprop='name']/a/@href"))
        street_address = "".join(
            d.xpath(".//span[@itemprop='streetAddress']/text()")
        ).strip()
        city = "".join(d.xpath(".//span[@itemprop='addressLocality']/text()")).strip()
        postal = "".join(d.xpath(".//span[@itemprop='postalCode']/text()")).strip()
        country_code = "BE"
        phone = "".join(d.xpath(".//span[@itemprop='telephone']/text()")).strip()
        hours_of_operation = ";".join(
            d.xpath(".//time[@itemprop='openingHours']/@datetime")
        )

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code=country_code,
            phone=phone,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://hector.be/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
