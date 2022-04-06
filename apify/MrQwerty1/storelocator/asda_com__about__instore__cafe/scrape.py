from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://storelocator.asda.com/sitemap.xml")
    tree = html.fromstring(r.content)

    return tree.xpath("//loc[contains(text(), '/cafe')]/text()")


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = " ".join(tree.xpath("//h1[@itemprop='name']/span/text()")).strip()
    street_address = ", ".join(
        tree.xpath("//a[contains(@class, 'c-address-street-')]/text()")
    ).strip()
    city = "".join(tree.xpath("//span[@class='c-address-city']/text()")).strip()
    postal = "".join(
        tree.xpath("//span[@class='c-address-postal-code']/text()")
    ).strip()

    phone = "".join(tree.xpath("//div[@id='phone-main']/text()")).strip()
    latitude = "".join(set(tree.xpath("//meta[@itemprop='latitude']/@content")))
    longitude = "".join(set(tree.xpath("//meta[@itemprop='longitude']/@content")))

    _tmp = []
    hours = tree.xpath("//table[@class='c-hours-details']/tbody/tr")
    for h in hours:
        day = "".join(h.xpath("./td[1]/text()"))
        inter = " ".join("".join(h.xpath("./td[2]//text()")).split())
        _tmp.append(f"{day}: {inter}")

    hours_of_operation = ";".join(_tmp)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
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
    locator_domain = "https://www.asda.com/about/instore/cafe"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
