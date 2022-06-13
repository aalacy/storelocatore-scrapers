from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://stores.kohler.com/en/locations/signature-stores")
    tree = html.fromstring(r.text)

    return tree.xpath("//a[@class='ksslocationcards--store-link']/@href")


def get_data(url, sgw: SgWriter):
    if url.startswith("/"):
        page_url = f"https://stores.kohler.com{url}"
    else:
        page_url = url

    r = session.get(page_url)
    tree = html.fromstring(r.text)
    location_name = "".join(tree.xpath("//div[@class='hidden']/text()")).strip()
    street_address = "".join(
        tree.xpath("//span[@itemprop='streetAddress']/text()")
    ).strip()
    city = "".join(tree.xpath("//span[@itemprop='addressLocality']/text()")).strip()
    state = "".join(tree.xpath("//span[@itemprop='addressRegion']/text()")).strip()
    postal = "".join(tree.xpath("//span[@itemprop='postalCode']/text()")).strip()
    text = "".join(tree.xpath("//script[contains(text(), 'countryCode')]/text()"))
    country_code = text.split('countryCode: "')[1].split('"')[0].upper().strip()
    store_number = "".join(tree.xpath("//input[@id='bpnumber']/@value")[0])
    phone = "".join(tree.xpath("//a[contains(@href, 'tel:')]/text()")).strip()

    _tmp = []
    hours = tree.xpath("//div[@class='sh-cal-row']")

    for h in hours:
        day = "".join(h.xpath("./div[1]/text()")).strip()
        time = "".join(h.xpath("./div[2]/text()")).strip()
        _tmp.append(f"{day}: {time}")

    if not hours:
        hours = tree.xpath("//div[@class='opening-time']/input")

        for h in hours:
            day = "".join(h.xpath("./@data-day"))
            time = "".join(h.xpath("./@data-time"))
            _tmp.append(f"{day}: {time}")

    hours_of_operation = ";".join(_tmp)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code=country_code,
        store_number=store_number,
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
    locator_domain = "https://stores.kohler.com/en/locations/signature-stores"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
