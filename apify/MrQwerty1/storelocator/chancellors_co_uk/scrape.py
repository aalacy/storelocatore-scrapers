from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://www.chancellors.co.uk/branches/")
    tree = html.fromstring(r.text)

    return tree.xpath("//a[@class='tabs-container__content--more-info']/@href")


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = tree.xpath("//h1/text()")[-1].strip()
    street_address = tree.xpath("//li[@itemprop='streetAddress']/text()")[0].strip()
    city = tree.xpath("//li[@itemprop='addressLocality']/text()")[0].strip()
    state = tree.xpath("//li[@itemprop='addressRegion']/text()")[0].strip()
    postal = tree.xpath("//li[@itemprop='postalCode']/text()")[0].strip()
    if postal[-1] == ",":
        postal = postal[:-1]
    phones = tree.xpath("//a[@class='single-branches__contact-info--tel']/text()")
    phones = list(filter(None, [ph.strip() for ph in phones]))
    phone = phones.pop(0)
    latitude = tree.xpath("//meta[@itemprop='latitude']/@content")[0]
    longitude = tree.xpath("//meta[@itemprop='longitude']/@content")[0]

    _tmp = []
    hours = tree.xpath(
        "//div[@class='tabs-container__content--opening-times' and .//strong[contains(text(), 'Office')]]//li"
    )
    for h in hours:
        _tmp.append(" ".join("".join(h.xpath(".//text()")).split()))

    hours_of_operation = ";".join(_tmp)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="GB",
        latitude=latitude,
        longitude=longitude,
        phone=phone,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.chancellors.co.uk/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
