from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    urls = list()
    r = session.get("https://local.pharmacy.vons.com/sitemap.xml")
    tree = html.fromstring(r.content)
    links = tree.xpath("//loc/text()")
    for link in links:
        if link.count("/") == 5:
            urls.append(link)

    return urls


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    a = tree.xpath("//h2[contains(text(), 'Pharmacy Info')]/following-sibling::div[1]")[
        0
    ]
    street_address = "".join(
        a.xpath(".//span[@class='c-address-street-1']/text()")
    ).strip()
    city = "".join(a.xpath(".//span[@class='c-address-city']/text()")).strip()
    state = "".join(a.xpath(".//abbr[@class='c-address-state']/text()")).strip()
    postal = "".join(a.xpath(".//span[@class='c-address-postal-code']/text()")).strip()

    location_name = f"Vons Pharmacy, {city}"
    phone = "".join(
        tree.xpath(
            "//div[contains(text(), 'Pharmacy Phone')]/following-sibling::div[1]/div/text()"
        )
    ).strip()
    latitude = "".join(tree.xpath("//meta[@itemprop='latitude']/@content"))
    longitude = "".join(tree.xpath("//meta[@itemprop='longitude']/@content"))

    _tmp = []
    hours = tree.xpath(
        "//h2[contains(text(), 'Pharmacy Hours')]/following-sibling::div[1]//tr[not(./th)]"
    )
    for h in hours:
        inters = []
        day = " ".join("".join(h.xpath("./td[1]//text()")).split())
        span = h.xpath("./td[2]/span")
        if not span:
            inters.append("Closed")

        for s in span:
            inter = " ".join("".join(s.xpath(".//text()")).split())
            inters.append(inter)
        _tmp.append(f'{day}: {"&".join(inters)}')

    hours_of_operation = ";".join(_tmp)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="US",
        location_type="Pharmacy",
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
    locator_domain = "https://vons.com/pharmacy.html"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
