from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_hours(page_url):
    _tmp = []
    r = session.get(page_url, headers=headers)
    if r.status_code == 301:
        return ""

    tree = html.fromstring(r.text)
    divs = tree.xpath("//h3[./div[contains(text(), 'Hours')]]/following-sibling::ul/li")
    for d in divs:
        day = "".join(d.xpath("./span[1]/text()")).strip()
        inter = "".join(d.xpath("./span[2]/text()")).strip()
        _tmp.append(f"{day}: {inter}")

    return ";".join(_tmp)


def fetch_data(sgw: SgWriter):
    api = "https://www.hendrickcars.com/hendrick-collision.htm"

    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//ol[@id='proximity-dealer-list']//div[@class='vcard']")

    for d in divs:
        location_name = "".join(d.xpath(".//a[@class='url']/span/text()")).strip()
        page_url = "".join(d.xpath(".//a[@class='url']/@href"))
        street_address = "".join(
            d.xpath(".//span[@class='street-address']/text()")
        ).strip()
        city = "".join(d.xpath(".//span[@class='locality']/text()")).strip()
        state = "".join(d.xpath(".//span[@class='region']/text()")).strip()
        postal = "".join(d.xpath(".//span[@class='postal-code']/text()")).strip()
        phone = "".join(d.xpath(".//span[@data-phone-ref='SALES']/text()")).strip()
        latitude = "".join(d.xpath(".//span[@class='latitude']/text()")).strip()
        longitude = "".join(d.xpath(".//span[@class='longitude']/text()")).strip()
        hours_of_operation = get_hours(page_url)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="US",
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    locator_domain = "https://www.hendrickcars.com/"
    with SgRequests() as session:
        with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
            fetch_data(writer)
