from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://www.familyshopperstores.co.uk/sitemap.xml")
    tree = html.fromstring(r.content)

    return tree.xpath("//loc[contains(text(), '/our-stores/')]/text()")


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text.replace("og:", ""))

    location_name = "".join(tree.xpath("//h1/text()")).strip()
    street_address = "".join(tree.xpath("//meta[@property='street_address']/@content"))
    if street_address.endswith(","):
        street_address = street_address[:-1]
    phone = "".join(
        tree.xpath("//p[@class='row']/a[contains(@href, 'tel:')]/text()")
    ).strip()
    city = "".join(tree.xpath("//meta[@property='locality']/@content"))
    state = "".join(tree.xpath("//meta[@property='region']/@content"))
    postal = "".join(tree.xpath("//meta[@property='postal_code']/@content"))

    latitude = tree.xpath("//meta[@property='latitude']/@content")[0]
    longitude = tree.xpath("//meta[@property='longitude']/@content")[0]

    _tmp = []
    tr = tree.xpath("//tr[@class='openingHours']")
    for t in tr:
        day = "".join(t.xpath("./td[1]/text()")).strip()
        inter = "".join(t.xpath("./td[2]/text()")).strip()
        _tmp.append(f"{day} {inter}")
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
    locator_domain = "https://www.familyshopperstores.co.uk/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
