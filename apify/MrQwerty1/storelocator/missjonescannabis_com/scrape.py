from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()
    city = adr.city or ""
    state = adr.state or SgRecord.MISSING
    postal = adr.postcode

    return street_address, city, state, postal


def get_additional(page_url):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    _tmp = []
    hours = tree.xpath("//ul[@class='location-hours']/li")
    for h in hours:
        day = "".join(h.xpath("./div[1]/text()")).strip()
        inter = "".join(h.xpath("./div[2]/text()")).strip()
        _tmp.append(f"{day}: {inter}")
    phone = "".join(tree.xpath("//a[contains(@href, 'tel:')]/text()")).strip()
    if tree.xpath("//strong[contains(text(), 'COMING SOON')]"):
        _tmp.append("Coming Soon")

    return phone, ";".join(_tmp)


def fetch_data(sgw: SgWriter):
    r = session.get(locator_domain, headers=headers)
    tree = html.fromstring(r.text)

    divs = tree.xpath("//li[@class='location-list-item']")
    for d in divs:
        location_name = "".join(
            d.xpath(".//div[@class='location-list-item-name']/a/text()")
        ).strip()
        page_url = "".join(d.xpath(".//div[@class='location-list-item-name']/a/@href"))
        raw_address = "".join(d.xpath(".//address/text()")).strip()
        street_address, city, state, postal = get_international(raw_address)
        if state == SgRecord.MISSING and "-on/" in page_url:
            state = "ON"
        latitude = "".join(d.xpath("./@data-lat"))
        longitude = "".join(d.xpath("./@data-lng"))
        phone, hours_of_operation = get_additional(page_url)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="CA",
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://missjonescannabis.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "cross-site",
        "Cache-Control": "max-age=0",
        "TE": "trailers",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
