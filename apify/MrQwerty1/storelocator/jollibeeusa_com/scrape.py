from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    urls = []
    r = session.get("https://locations.jollibeeusa.com/sitemap.xml")
    tree = html.fromstring(r.content)
    links = tree.xpath("//loc/text()")
    for link in links:
        if link.count("/") == 6:
            urls.append(link)

    return urls


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1[@itemprop='name']/text()")).strip()
    street_address = ", ".join(
        tree.xpath(
            "//div[@class='Address Hero-address']//span[contains(@class, 'Address-field Address-line')]/text()"
        )
    ).strip()
    city = "".join(
        tree.xpath("//span[@class='Address-field Address-city']/text()")
    ).strip()
    state = "".join(
        tree.xpath(
            "//span[contains(@class, 'Address-field Address-region Address-region')]/text()"
        )
    ).strip()
    postal = "".join(
        tree.xpath("//span[@class='Address-field Address-postalCode']/text()")
    ).strip()
    if "/usa/" in page_url:
        country_code = "US"
    else:
        country_code = "CA"
    phone = "".join(
        tree.xpath("//span[@class='Text Phone-text Phone-display']/text()")
    ).strip()

    latitude = "".join(tree.xpath("//meta[@itemprop='latitude']/@content"))
    longitude = "".join(tree.xpath("//meta[@itemprop='longitude']/@content"))

    _tmp = []
    hours = tree.xpath(
        "//div[contains(text(), 'Store Hours')]/following-sibling::div//tr[contains(@class, 'c-hours-details-row js-day-of-week-row highlight-text')]"
    )

    for h in hours:
        day = "".join(h.xpath("./td[1]//text()")).strip()
        inter = " ".join("".join(h.xpath("./td[2]//text()")).split())
        _tmp.append(f"{day}: {inter}")

    hours_of_operation = ";".join(_tmp)
    if "coming" in location_name.lower():
        hours_of_operation = "Coming Soon"
    if hours_of_operation.count("Closed") == 7:
        return

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


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://jollibeeusa.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
